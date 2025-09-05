from agent.Agent import Agent


def main():
    try:
        agent = Agent()
        agent.ask_question()
    except Exception as e:
        print(f"Erorr: {e}")


if __name__ == "__main__":
    main()
