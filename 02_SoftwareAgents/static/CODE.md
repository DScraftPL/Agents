```python
class GreetingApp:
    def show_hello_world(self):
        print("Hello, World!")

    def show_goodbye_world(self):
        print("Goodbye, World!")

    def start(self):
        self.show_hello_world()
        while True:
            user_input = input("Type 'exit' to quit or press Enter to continue: ")
            if user_input.lower() == 'exit':
                print("Exiting the application.")
                break
            else:
                self.show_goodbye_world()

if __name__ == "__main__":
    app = GreetingApp()
    app.start()
```