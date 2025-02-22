import time
import threading
from tqdm import tqdm
from collections import deque
from typing import Dict, List, Tuple
from read_csv import read_process_from_csv
from concurrent.futures import ThreadPoolExecutor


# Define available resources
RESOURCE_TYPES = {"inc", "out", "add", "smp", "arm"}


class Resource:
    """Handles a specific resource type, managing a queue of operations."""
    
    def __init__(self, name: str, max_workers: int = 1):
        self.name = name
        self.active = False
        self.queue = deque()
        self._stopping = False
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=f"Resource-{name}")

    def request(self, process_id: int, operation: str, duration: List[int], event: threading.Event):
        """Request access to a resource, enqueue if busy."""
        with self.condition:
            if self.name == "arm" and operation == "0x500":
                self.queue.append( (process_id, "0x500", duration[0], None) )
                self.queue.append( (process_id, "0x600", duration[1], event) )
            else:
                self.queue.append((process_id, operation, duration[0], event))
            if not self.active:
                self.condition.notify_all()
                self.__process_next()

    def __process_next(self) -> None:
        """Process the next operation in the queue."""
        if self._stopping or not self.queue:
            return
        
        self.active = True
        process_id, operation, duration, event = self.queue.popleft()
        future = self.executor.submit(
            self.__execute,
            process_id,
            operation,
            duration,
            event
        )
        future.add_done_callback(self.__operation_completed)

    def __execute(self, process_id: int, operation: str, duration: int, event: threading.Event):
        """Executes the operation and notifies the next in queue."""
        try:
            time.sleep(duration / 1000)  # Simulate execution
        finally:
            if event:
                event.set()
    
    def __operation_completed(self, future):
        if future.exception():
            raise Exception(f"Opeartion Failed : {future.exception()}")

        with self.condition:
            if not self.queue:
                self.active = False
            else:
                self.__process_next()
    
    def shutdown(self):
        """Clean shutdown of resource."""
        self._stopping = True
        self.executor.shutdown(wait=True)



class Process:
    """Handles the execution of a process with multiple operations."""
    
    def __init__(self, process_id: int, operations: List[Tuple], resource_manager: Dict):
        self.process_id = process_id
        self.operations = operations
        self.resource_manager = resource_manager
        self.start_time = None
        self.end_time = None

    def run(self):
        """Executes each operation sequentially using resource requests."""

        try:
            progress_bar = tqdm(total=len(self.operations), desc=f"Process {self.process_id}")
            self.start_time = int( time.time() * 1000)
            i = 0
            while i < len(self.operations):
                resource_type, operation, duration = self.operations[i]
                duration = [duration]
                resource = self.resource_manager[resource_type]
                event = threading.Event()
                if resource_type == "arm" and operation == "0x500":
                    i += 1
                    duration.append(self.operations[i][2])
                    progress_bar.update(1)
                resource.request(self.process_id, operation, duration, event)
                event.wait()
                i += 1
                progress_bar.update(1)
                # print(f"Process {self.process_id} - {resource_type} - {operation} - {duration[0]} ms")
            self.end_time = int( time.time() * 1000 )
        except Exception as e:
            print(f"Error executing process - {self.process_id} - {e}")
        finally:
            progress_bar.close()


    

    def get_downtime(self):
        """Calculates the downtime for each resource within the process."""
        if self.end_time is None:
            return {}   # Process is still running
        
        total_time = self.end_time - self.start_time
        downtime = { res: total_time for res in self.resource_manager.keys()}
        for resource_type, _, duration in self.operations:
            downtime[resource_type] -= duration
        return downtime


def schedule_processes(files: List[str]):
    """Schedules all processes with proper resource management."""
    try:
        processes = {}
        resource_manager = {res: Resource(res) for res in RESOURCE_TYPES}
        for i, file in enumerate(files):
            processes[i] = Process(i, read_process_from_csv(file), resource_manager)

        threads = []
        for process in processes.values():
            thread = threading.Thread(target=process.run)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Displaying downtime for each process - Addresses Quesntion 2
        for process in processes.values():
            print(f"Process {process.process_id} finished in {process.end_time - process.start_time} ms")
            print(f"Downtime for Process {process.process_id}: {process.get_downtime()}")

        # Displaying total Cluster Time - Addresses Quesntion 3
        start_time = min(p.start_time for p in processes.values() if p.start_time is not None)
        end_time = max(p.end_time for p in processes.values() if p.end_time is not None)

        print(f"Total Cluster Time: {end_time - start_time}")

    finally:
        # Ensure proper cleanup
        for resource in resource_manager.values():
            resource.shutdown()

if __name__ == "__main__":
    process_files = ["grex_process_1.csv", "grex_process_2.csv", "grex_process_3.csv"]
    schedule_processes(process_files)
