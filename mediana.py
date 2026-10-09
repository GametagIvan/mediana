from flask import Flask, request, redirect, url_for
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statistics
import io
import base64
from html import escape

app = Flask(__name__)
experiments = []


def graph():
    if not experiments:
        return ""
    labels = [
        f"{e['wifi']} / {e['distance']:g} м"
        for e in experiments
    ]
    values = [e["median"] for e in experiments]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(
        range(len(values)),
        values,
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=7
    )
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Медианная задержка (мс)")
    ax.set_title("Задержка ввода CS2")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")

@app.route("/", methods=["GET", "POST"])
def home():
    error = ""
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "clear":
            experiments.clear()
            return redirect(url_for("home"))
        try:
            wifi = request.form["wifi"]
            distance = float(request.form["distance"])
            nums = [
                float(n) for n in request.form["nums"].split()
            ]
            if (
                wifi not in ("2.4 ГГц", "5 ГГц")
                or not 0 <= distance <= 50
                or not nums
                or any(n < 0 for n in nums)
            ):
                raise ValueError
            experiments.append({
                "wifi": wifi,
                "distance": distance,
                "values": nums,
                "median": statistics.median(nums)
            })
            return redirect(url_for("home"))
        except (ValueError, KeyError):
            error = "Проверь расстояние и измерения."
    rows = "".join(
        f"<tr><td>{i}</td><td>{e['wifi']}</td>"
        f"<td>{e['distance']:g} м</td>"
        f"<td>{escape(' '.join(map(str, e['values'])))}</td>"
        f"<td>{e['median']:g} мс</td></tr>"
        for i, e in enumerate(experiments, 1)
    )
    image = graph()
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>Задержка ввода CS2</title>
    </head>
    <body style="
        background:#20172e;
        color:white;
        font-family:Arial,sans-serif;
        max-width:850px;
        margin:30px auto;
        padding:15px;
    ">
    <h1>Задержка ввода CS2</h1>
    <form method="post"
          style="background:#2c2340;padding:20px;border-radius:10px">
        <input type="hidden" name="action" value="add">
        <p>Wi-Fi:
            <select name="wifi">
                <option>2.4 ГГц</option>
                <option>5 ГГц</option>
            </select>
        </p>
        <p>Расстояние (м):<br>
            <input type="number" name="distance"
                   min="0" max="50" step="any"
                   value="1" required>
        </p>
        <p>Измерения в мс (через пробел):<br>
            <input name="nums"
                   placeholder="18 21 19 24 20"
                   required>
        </p>
        <button type="submit">Добавить эксперимент</button>
    </form>
    <p style="color:#ffaaaa">{escape(error)}</p>
    <h2>Результаты</h2>
    <div style="overflow-x:auto">
        <table border="1" cellpadding="8">
            <tr>
                <th>№</th>
                <th>Wi-Fi</th>
                <th>Расстояние</th>
                <th>Измерения</th>
                <th>Медиана</th>
            </tr>
            {rows}
        </table>
    </div>
    {
        "<h2>График</h2><img style='max-width:100%' src='data:image/png;base64,"
        + image + "'>"
        if image else "<p>Пока нет замеров и графика.</p>"
    }
    <form method="post"
          onsubmit="return confirm('Удалить все замеры?');"
          style="margin-top:15px">

        <input type="hidden" name="action" value="clear">

        <button type="submit"
                style="
                    background:#d93650;
                    color:white;
                    border:none;
                    padding:7px 12px;
                    border-radius:6px;
                    font-size:13px;
                    cursor:pointer;
                ">
            Удалить все замеры
        </button>
    </form>

    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(debug=False)



#python3.13 mediana.py
