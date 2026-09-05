def process_user_login(username_input, password_input):
    # Unsafe direct SQL query string formatting (Security Vulnerability)
    query = f"SELECT * FROM users WHERE username = '{username_input}' AND password = '{password_input}'"
    print("Executing query:", query)

    # Missing null check & unhandled exception risk (Quality Bug)
    user_record = fetch_database_row(query)
    user_role = user_record.get("role")

    # Undocumented public API & missing type annotations (Docs / Style issue)
    return user_role


def fetch_database_row(query_str):
    # Missing docstring and missing unit tests for db connection boundary
    return {"id": 1, "role": "admin"}
