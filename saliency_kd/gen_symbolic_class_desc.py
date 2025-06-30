#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import numpy as np
from openai import OpenAI

from saliency_kd.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from saliency_kd.secret_config import OPENAI_API_KEY

INIT_PROMPT = "There is a number of signals:"
MODE_PROMPT_TS = "\n\nIn the following separated lists of values, describe each list, i.e., signal, in a similar fashion to the following symbolic description example."
SYMBOLIC_EXAMPLE = "\n\nexample_class: starting low, slowly but steadily going up to a positive peak or plateau, afterwards down again, very straight plateau, then going upwards to a noisy peak"
# before: Describe them at the same granularity as the example above. Don't use raw values - indicating that values are positive or negative is feasible, but no exact values.
# PROMPT_APPENDIX = "\n\nDescribe them at the same granularity as the example above. Don't use raw values and also not whether values are positive or negative, just describe the overall shape."
# PROMPT_APPENDIX = "\n\nDescribe them at roughly the same granularity as the example above."

# removed: (as brief as possible)
PROMPT_APPENDIX = "\n\nDescribe them at roughly the same granularity as the example above and in a way in which symbolic fault descriptions of known anomalies for some signal types stored in a database could realistically look like. Don't use raw values - indicating that values are positive or negative is feasible, but no exact value."


class LLMSymbolicDescGen:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.kgqt = KnowledgeGraphQueryTool()

    def prompt_gpt(self, input_prompt):
        # TODO: think about max_tokens argument (!)
        response = self.client.responses.create(
            # model="gpt-4.1",
            # model="gpt-4.1-2025-04-14",
            # model="gpt-4o", # works
            model="o3-2025-04-16",  # --> best, but expensive
            # model="gpt-4o-mini",
            # max_tokens=300, # controlling costs (meant for responses)
            input=input_prompt
        )
        print("response..")
        print(response.id)
        print(response.model)
        print(response.output_text)
        print(response.temperature)
        print(response.max_output_tokens)
        print(response.usage)

        # TODO: test those
        # print(response.usage.input_tokens)
        # print(response.usage.output_tokens)
        # print(response.usage.total_tokens)

        return response.output_text.split("\n")[-1]

    @staticmethod
    def get_medoids_ts():
        return np.load("medoids4llm.npy")

    def gen_prompt_ts(self):
        arr = self.get_medoids_ts()
        medoid_lst = [" ".join([str(round(v, 2)) for v in c.tolist()]) for i, c in enumerate(arr)]
        str_medoids = "\n\n".join(f"signal {i + 1}:\n{c}" for i, c in enumerate(medoid_lst))

        prompt = INIT_PROMPT + MODE_PROMPT_TS + SYMBOLIC_EXAMPLE + PROMPT_APPENDIX + "\n\n" + str_medoids
        print("-----------------------------------------------------")
        print("prompt..\n", prompt)
        print("-----------------------------------------------------")
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                ]
            }
        ]


if __name__ == "__main__":
    llm_sym_desc_gen = LLMSymbolicDescGen()
    output = llm_sym_desc_gen.prompt_gpt(llm_sym_desc_gen.gen_prompt_ts())
    print("output:", output)
