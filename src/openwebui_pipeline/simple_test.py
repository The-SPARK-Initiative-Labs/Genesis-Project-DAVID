"""
title: Simple Test
author: test
version: 1.0.0
description: Minimal test pipeline
"""

from typing import Union, Generator, Iterator
from pydantic import BaseModel

class Pipeline:
    def __init__(self):
        self.type = "pipe"
        self.id = "simple_test"
        self.name = "Simple Test"

    def pipe(self, body: dict) -> Union[str, Generator, Iterator]:
        messages = body.get("messages", [])
        if messages:
            last_message = messages[-1].get("content", "")
            return f"Echo: {last_message}"
        return "No message received"
