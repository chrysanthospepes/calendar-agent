from app.agent.calendar_agent import CalendarAgent

def main():
    agent = CalendarAgent()
    prompt = input("What would you like to schedule?\n> ")
    result = agent.run(prompt)
    print(result)

if __name__ == "__main__":
    main()
