class QuizPoll:
    def __init__(self, data):
        self.data: dict = data
        self.type: str = data.get("type")
        self.module: str = data.get("module")

    def get_poll_parameters(self) -> list:
        poll_list = []
        questions: list = self.data.get("questions")

        for question in questions:
            poll_q = self.convert_q_to_poll(question)
            poll_list.append(poll_q)

        return poll_list

    # returns a dict compatible with send poll func
    def convert_q_to_poll(self, question: dict) -> dict:
        new_q = {}
        new_q["question"] = question.get("question")
        opt_list = []
        for opt in ["a", "b", "c", "d"]:
            opt_list.append(question.get(opt))
        new_q["options"] = opt_list
        new_q["type"] = "quiz"
        new_q["correct_option_id"] = ord(question.get("answer")) - ord("a")
        new_q["is_anonymous"] = True

        return new_q
