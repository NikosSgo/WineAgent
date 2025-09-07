def print_citations(result):
    for citation in result.citations:
        for source in citation.sources:
            if source.type != "filechunk":
                continue
            print("------------------------")
            print(source.parts[0])


class Agent:
    def __init__(
        self,
        sdk,
        model,
        assistant=None,
        instruction=None,
        search_index=None,
        tools=None,
    ):
        self.thread = None
        self.sdk = sdk
        if assistant:
            self.assistant = assistant
        else:
            if tools:
                self.tools = {x.__name__: x for x in tools}
                tools = [sdk.tools.function(x) for x in tools]
            else:
                self.tools = {}
                tools = []
            if search_index:
                tools.append(sdk.tools.search_index(search_index))
            self.assistant = self.create_assistant(model, tools)

        if instruction:
            self.assistant.update(instruction=instruction)

    def get_thread(self, thread=None):
        if thread is not None:
            return thread
        if self.thread is None:
            self.thread = self.sdk.threads.create(
                ttl_days=1, expiration_policy="static"
            )
        return self.thread

    def __call__(self, message, thread=None):
        thread = self.get_thread(thread)
        thread.write(message)
        run = self.assistant.run(thread)
        res = run.wait()
        if res.tool_calls:
            result = []
            for f in res.tool_calls:
                print(f" + Вызываем функцию {f.function.name}, args={f.function.arguments}")
                fn = self.tools[f.function.name]
                obj = fn(**f.function.arguments)
                x = obj.process(thread)
                result.append({"name": f.function.name, "content": x})
            run.submit_tool_results(result)
            # time.sleep(3)
            res = run.wait()
            print_citations(res)
        return res.text

    def restart(self):
        if self.thread:
            self.thread.delete()
            self.thread = self.sdk.threads.create(
                name="Test", ttl_days=1, expiration_policy="static"
            )

    def done(self, delete_assistant=False):
        if self.thread:
            self.thread.delete()
        if delete_assistant:
            self.assistant.delete()

    def create_assistant(self, model, tools=None):
        kwargs = {}
        if tools and len(tools) > 0:
            kwargs = {"tools": tools}
        return self.sdk.assistants.create(
            model, ttl_days=1, expiration_policy="since_last_active", **kwargs
        )
