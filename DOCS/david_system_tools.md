# DAVID AI - COMPLETE SYSTEM TOOLS LIST
## Native LangGraph @tool decorators for full PC control

### FILE OPERATIONS
- `read_file(path)` - Read any file content
- `write_file(path, content)` - Write/overwrite file content
- `append_file(path, content)` - Append to existing file
- `edit_line(path, line_number, new_content)` - Edit specific line
- `find_replace(path, find, replace, regex=False)` - Find/replace text
- `delete_file(path)` - Delete file
- `copy_file(source, destination)` - Copy file
- `move_file(source, destination)` - Move/rename file
- `file_exists(path)` - Check if file exists
- `file_info(path)` - Get file metadata (size, dates, permissions)
- `file_permissions(path, permissions)` - Change file permissions
- `file_search(directory, pattern)` - Search for files by pattern
- `file_hash(path, algorithm='md5')` - Generate file hash

### DIRECTORY OPERATIONS
- `list_directory(path)` - List directory contents
- `create_directory(path)` - Create directory
- `delete_directory(path, recursive=False)` - Delete directory
- `copy_directory(source, destination)` - Copy entire directory
- `move_directory(source, destination)` - Move directory
- `directory_exists(path)` - Check if directory exists
- `directory_size(path)` - Calculate directory size
- `find_directories(root, pattern)` - Find directories by pattern
- `directory_tree(path, max_depth=None)` - Get directory tree structure
- `change_directory(path)` - Change working directory
- `get_current_directory()` - Get current working directory

### SYSTEM COMMANDS
- `execute_command(command, working_dir='.', timeout=30)` - Run any system command
- `execute_powershell(script, working_dir='.', timeout=30)` - Run PowerShell commands
- `execute_batch(script, working_dir='.', timeout=30)` - Run batch scripts
- `run_as_admin(command)` - Execute with administrator privileges
- `get_command_output(command)` - Get command output only
- `background_command(command)` - Run command in background
- `kill_command(pid)` - Kill running command by PID

### PROCESS MANAGEMENT
- `list_processes()` - List all running processes
- `process_info(pid_or_name)` - Get detailed process information
- `start_process(executable, args=None, working_dir=None)` - Start new process
- `kill_process(pid_or_name)` - Terminate process
- `process_exists(name)` - Check if process is running
- `process_cpu_usage(pid)` - Get CPU usage for process
- `process_memory_usage(pid)` - Get memory usage for process
- `set_process_priority(pid, priority)` - Change process priority
- `process_threads(pid)` - List process threads
- `process_environment(pid)` - Get process environment variables

### NETWORK OPERATIONS
- `ping_host(target, count=4)` - Ping network host
- `nslookup(hostname)` - DNS lookup
- `traceroute(target)` - Trace network route
- `netstat(options='')` - Network connection status
- `port_scan(host, port_range)` - Scan for open ports
- `download_file(url, destination)` - Download file from URL
- `upload_file(file_path, url)` - Upload file to URL
- `http_request(url, method='GET', headers=None, data=None)` - Make HTTP requests
- `network_interfaces()` - List network interfaces
- `network_speed_test()` - Test internet speed

### REGISTRY ACCESS (Windows)
- `registry_read(key_path, value_name)` - Read registry value
- `registry_write(key_path, value_name, value, value_type)` - Write registry value
- `registry_delete(key_path, value_name=None)` - Delete registry key/value
- `registry_list_keys(key_path)` - List registry subkeys
- `registry_list_values(key_path)` - List registry values
- `registry_export(key_path, file_path)` - Export registry to file
- `registry_import(file_path)` - Import registry from file

### HARDWARE ACCESS
- `system_info(info_type='all')` - Get hardware information
- `cpu_usage()` - Get CPU usage percentage
- `memory_usage()` - Get RAM usage information
- `disk_usage(drive='C:')` - Get disk space information
- `disk_list()` - List all disk drives
- `temperature_sensors()` - Get hardware temperatures
- `battery_status()` - Get battery information (laptops)
- `usb_devices()` - List USB devices
- `monitor_info()` - Get monitor/display information

### USER INTERFACE AUTOMATION
- `screenshot(file_path=None)` - Take screenshot
- `click_coordinates(x, y)` - Click at specific coordinates
- `type_text(text)` - Type text at current cursor
- `key_combination(keys)` - Send key combinations (Ctrl+C, etc.)
- `window_list()` - List open windows
- `window_focus(window_title)` - Focus specific window
- `window_close(window_title)` - Close specific window
- `window_minimize(window_title)` - Minimize window
- `window_maximize(window_title)` - Maximize window

### SERVICE MANAGEMENT
- `list_services()` - List Windows services
- `service_status(service_name)` - Get service status
- `start_service(service_name)` - Start Windows service
- `stop_service(service_name)` - Stop Windows service
- `restart_service(service_name)` - Restart Windows service
- `service_startup_type(service_name, startup_type)` - Change service startup type

### ENVIRONMENT & SYSTEM
- `environment_variables()` - List environment variables
- `set_environment_variable(name, value)` - Set environment variable
- `get_environment_variable(name)` - Get environment variable
- `system_uptime()` - Get system uptime
- `logged_in_users()` - List logged in users
- `system_reboot(delay=0)` - Reboot system
- `system_shutdown(delay=0)` - Shutdown system
- `system_sleep()` - Put system to sleep
- `lock_workstation()` - Lock the workstation

### PROGRAMMING LANGUAGE EXECUTION
- `python_execute(code, file_path='', timeout=30)` - Execute Python code
- `node_execute(code, file_path='')` - Execute JavaScript/Node.js
- `java_execute(file_path, class_name)` - Execute Java programs
- `csharp_execute(code, references=None)` - Execute C# code
- `powershell_execute(script)` - Execute PowerShell scripts
- `batch_execute(script)` - Execute batch scripts
- `compile_code(source_file, language, output_file)` - Compile source code

### DATABASE OPERATIONS
- `sqlite_query(db_path, query)` - Execute SQLite queries
- `sqlite_create_table(db_path, table_name, schema)` - Create SQLite table
- `csv_to_sqlite(csv_path, db_path, table_name)` - Import CSV to SQLite
- `database_backup(db_path, backup_path)` - Backup database
- `database_restore(backup_path, db_path)` - Restore database

### COMPRESSION & ARCHIVES
- `create_zip(files, zip_path)` - Create ZIP archive
- `extract_zip(zip_path, destination)` - Extract ZIP archive
- `create_tar(files, tar_path)` - Create TAR archive
- `extract_tar(tar_path, destination)` - Extract TAR archive
- `compress_file(file_path, algorithm='gzip')` - Compress single file
- `decompress_file(file_path, destination)` - Decompress file

### SYSTEM MONITORING
- `monitor_cpu(duration=60)` - Monitor CPU usage over time
- `monitor_memory(duration=60)` - Monitor memory usage over time
- `monitor_disk_io(duration=60)` - Monitor disk I/O
- `monitor_network(duration=60)` - Monitor network traffic
- `system_logs(log_type='system', count=100)` - Read system logs
- `performance_counters(counter_name)` - Get Windows performance counters

### SCHEDULED TASKS
- `list_scheduled_tasks()` - List Windows scheduled tasks
- `create_scheduled_task(name, command, schedule)` - Create scheduled task
- `delete_scheduled_task(name)` - Delete scheduled task
- `run_scheduled_task(name)` - Run scheduled task immediately
- `task_status(name)` - Get scheduled task status

### SECURITY & PERMISSIONS
- `file_acl(path)` - Get file access control list
- `set_file_acl(path, acl)` - Set file permissions
- `user_groups(username)` - Get user group memberships
- `is_admin()` - Check if running as administrator
- `password_policy()` - Get password policy information
- `security_events(count=100)` - Get security event logs

### WINDOWS-SPECIFIC FEATURES
- `windows_features()` - List Windows features
- `enable_windows_feature(feature_name)` - Enable Windows feature
- `disable_windows_feature(feature_name)` - Disable Windows feature
- `installed_programs()` - List installed programs
- `uninstall_program(program_name)` - Uninstall program
- `windows_update_check()` - Check for Windows updates
- `windows_firewall_status()` - Get Windows Firewall status
- `add_firewall_rule(name, port, protocol)` - Add firewall rule