from app.agent.calendar_agent import CalendarAgent

def main():
    agent = CalendarAgent()
    
    while True:
        try:
            prompt = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("Exiting...")
            break
        
        if prompt == "exit":
            break
        
        result = agent.run(prompt)
        print(result)
    

if __name__ == "__main__":
    main()