"""
title: Test Pipeline
author: test
version: 1.0.0
description: Simple test pipeline
"""

from typing import Union, Generator, Optional
from pydantic import BaseModel, Field

class Pipeline:
    class Valves(BaseModel):
        test_param: str = Field(default="Hello from David!", description="Test parameter")

    def __init__(self):
        self.type = "pipe"
        self.id = "test_pipeline"
        self.name = "Test Pipeline"
        self.valves = self.Valves()

    def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[callable] = None
    ) -> Union[str, Generator]:
        
        messages = body.get("messages", [])
        last_message = messages[-1]["content"] if messages else "no message"
        
        response = f"{self.valves.test_param} You said: {last_message}"
        return response
