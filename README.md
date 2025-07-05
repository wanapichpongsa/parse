Simple parse bank statement pdf as string -> omit sensitive data via local llm -> mainstream llm interpret data structures for storing in db && aggregating same category data from multiple different sources

### Create your personal.py file

Example schema

```python
user_data: set[str] = {
  "fullname", "email", "address", "bankaccount_ids"
}

# if not present in page then don't append to final output
data_tokens: set[str] = {
    "date description inflow outflow balance"
}

# before | after refers to data you want is before or after a certain string token
page_data_breakpoints: dict[str, "before" | "after"] = {
    "Your spending activity": "after",
    "Why us": "before"
}
```
