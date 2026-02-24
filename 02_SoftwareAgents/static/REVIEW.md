Here is a review of the provided Python code:

### Code Structure and Functionality:
1. **Class Design**:
    - The class `GreetingApp` is well-structured with each function having a clear single responsibility.
    - The methods `show_hello_world` and `show_goodbye_world` serve straightforward purposes of displaying messages.

2. **Control Flow**:
    - The `start` method initiates the application by showing "Hello, World!" and then enters an infinite loop, waiting for user input to either exit or continue.
    - If the user types 'exit', the application exits; otherwise, it displays "Goodbye, World!".

### Potential Improvements:
1. **User Input Logic**:
    - The application could become more user-friendly by providing more options or using interactive commands. For instance, you can add more commands besides 'exit' and 'continue'.

2. **Infinite Loop**:
    - The code currently uses an infinite loop, which may not be the best practice in many applications unless absolutely necessary. Consider breaking the loop in other ways to make the application more maintainable.

3. **Handling Interrupts**:
    - This code is susceptible to interruption by the user (e.g., pressing `Ctrl+C`). Consider handling such exceptions to gracefully exit or perform cleanup tasks. For example:
      ```python
      try:
          app.start()
      except KeyboardInterrupt:
          print("\nApplication interrupted. Exiting...")
      ```

4. **Documentation and Comments**:
    - Adding docstrings or comments to explain the purpose of each method and the overall functionality of the class would help in maintaining the code.

5. **Input Validation**:
    - Currently, any input other than 'exit' results in the method `show_goodbye_world` being called. Consider validating input or providing feedback on unrecognized commands.

6. **Extensibility**:
    - If you plan to extend the functionality further, consider using a command pattern or handler functions to make adding new commands easier.

### Security Considerations:
- **Command Injection**: Although this code doesn't appear to take immediate external input that could cause command injection vulnerabilities, always be cautious about what and how inputs are handled when code evolves.

### Summary:
This is a nicely structured basic application with a clear goal. Implementing the improvements above would enhance its usability, maintainability, and robustness.