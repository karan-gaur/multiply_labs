# Process Scheduling System

## Assumptions

### Input Assumptions

1. All CSV files are expected to have a header followed by rows.
2. Each CSV file must follow the format: **Module, Operation, Operation Duration**.
3. Modules and operations are restricted to the values listed in **human_readable_information.csv**.
4. CSV file paths must be valid and present. The program does not handle errors for invalid file paths.

### Logical Assumptions

1. Once a process completes its operation on a module, it vacates the module immediately. Thus, there is no risk of deadlocks due to the **Hold & Wait** condition.
2. Each **PICK** operation in a process is always followed by a **PLACE** operation, ensuring that no process indefinitely holds a resource.
3. If an error occurs in any operation, the entire execution is blocked, and an error is raised.

---

## Answers to Key Questions

### **Question 1: How is process data stored?**

Each process is stored as an instance of a class object. For operations, a list is used for convenience, though a linked list could also be used.

### **Question 2: How is downtime displayed?**

After executing all threads, the execution time for each process and its respective downtime are displayed in the terminal.

### **Question 3: How is resource allocation managed?**

- The **PICK** operation of a process is always followed by the corresponding **PLACE** operation.
- The **First-Come-First-Served (FCFS)** scheduling algorithm is used.
- The modular code structure allows easy replacement with other scheduling algorithms if needed.

### **Question 4: How can additional process files be added?**

Additional CSV files can be added by including their paths in the `process_files` list in the script.

### **Question 5: What UI is best suited for this process?**

Currently, the terminal is the most effective interface for tracking process execution and progress. Given the nature of the system, a graphical UI does not provide significant advantages.

---

## Usage Instructions

0. Install the dependecies using requirements.txt (Although there is just 1)
   ```bash
   pip install requirements.txt
   
1. Ensure that all required CSV files are correctly formatted and placed in the designated directory.
2. Modify the `process_files` list in the script to include the desired files.
3. Run the script using Python.
   ```bash
   python3 soln.py
5. Observe the execution time and downtime statistics in the terminal.

---

## Author

Developed by Karan Gaur.
