
from flask import Flask, render_template, request, session
import ast
import math
import operator

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Only allow these mathematical operations.
OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression):
    """Calculate an expression without using eval()."""

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("π", "pi")

    tree = ast.parse(expression, mode="eval")

    def solve(node):
        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.Name) and node.id == "pi":
            return math.pi

        if isinstance(node, ast.BinOp):
            operation = OPERATIONS.get(type(node.op))
            if operation is None:
                raise ValueError("Invalid operation")

            left = solve(node.left)
            right = solve(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise ValueError("Cannot divide by zero")

            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Power too large")

            result = operation(left, right)

            if not math.isfinite(result) or abs(result) > 1e100:
                raise ValueError("Result out of range")

            return result

        if isinstance(node, ast.UnaryOp):
            operation = OPERATIONS.get(type(node.op))
            if operation is None:
                raise ValueError("Invalid operation")
            return operation(solve(node.operand))

        raise ValueError("Invalid expression")

    result = solve(tree)

    if not math.isfinite(result):
        raise ValueError("Invalid result")

    return result


@app.route("/", methods=["GET", "POST"])
def calculator():
    expression = session.get("expression", "")
    display = session.get("display", "0")
    error = ""

    if request.method == "POST":
        action = request.form.get("action", "")

        try:
            if action == "clear":
                expression = ""
                display = "0"

            elif action == "delete":
                expression = expression[:-1]
                display = expression or "0"

            elif action == "calculate":
                if expression:
                    result = safe_calculate(expression)
                    display = f"{result:.12g}"
                    expression = display

            elif action == "sqrt":
                result = safe_calculate(expression)
                if result < 0:
                    raise ValueError("Invalid square root")
                display = f"{math.sqrt(result):.12g}"
                expression = display

            elif action == "square":
                result = safe_calculate(expression)
                display = f"{result ** 2:.12g}"
                expression = display

            elif action == "percent":
                result = safe_calculate(expression)
                display = f"{result / 100:.12g}"
                expression = display

            elif action.startswith("add:"):
                value = action[4:]

                allowed = set("0123456789.+-*/()π")
                if all(char in allowed for char in value):
                    if len(expression) < 150:
                        expression += value
                    display = expression or "0"

        except (ValueError, SyntaxError, ZeroDivisionError,
                OverflowError, TypeError):
            error = "Invalid calculation"
            display = "Error"
            expression = ""

        session["expression"] = expression
        session["display"] = display

    return render_template(
        "index.html",
        expression=expression,
        display=display,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)

