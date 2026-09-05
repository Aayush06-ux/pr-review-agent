def execute_user_command(user_cmd):
    # Unsafe OS command execution risk (Security Vulnerability)
    import os
    os.system(user_cmd)

    # Missing null check & AttributeError risk (Quality Bug)
    result = user_cmd.get("output")
    return result


def process_response(resp):
    # Undocumented public function & missing test coverage
    return resp
