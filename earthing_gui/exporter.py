
import io
import base64
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
from .translations import t

def export_html(parent, results, network):
    if not results:
        messagebox.showwarning(t('export'), "No results to export.")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
    if not filepath:
        return

    # Generate Plots for export
    # Surface Potential
    fig1 = plt.Figure(figsize=(6, 5))
    ax1 = fig1.add_subplot(111)
    if network.Vg is not None:
        contour = ax1.contourf(network.XX, network.YY, network.Vg, 20, cmap="plasma")
        fig1.colorbar(contour, ax=ax1)
        ax1.set_title(t('plot_surface'))
    img1 = fig_to_base64(fig1)

    # Touch Voltage
    fig2 = plt.Figure(figsize=(6, 5))
    ax2 = fig2.add_subplot(111)
    if network.Vg is not None:
        gpr = results.get('gpr', 0)
        V_touch = gpr - network.Vg
        contour = ax2.contourf(network.XX, network.YY, V_touch, 20, cmap="Reds")
        fig2.colorbar(contour, ax=ax2)
        ax2.set_title(t('plot_touch'))
    img2 = fig_to_base64(fig2)

    # Step Voltage
    fig3 = plt.Figure(figsize=(6, 5))
    ax3 = fig3.add_subplot(111)
    if network.Vg is not None:
        import numpy as np
        dx = network.XX[0,1] - network.XX[0,0]
        dy = network.YY[1,0] - network.YY[0,0]
        Vy, Vx = np.gradient(network.Vg, dy, dx)
        V_step = np.sqrt(Vx**2 + Vy**2) * 1.0
        contour = ax3.contourf(network.XX, network.YY, V_step, 20, cmap="Oranges")
        fig3.colorbar(contour, ax=ax3)
        ax3.set_title(t('plot_step'))
    img3 = fig_to_base64(fig3)

    # Assess Safety
    touch_limit = results.get('e_touch_limit', 0)
    step_limit = results.get('e_step_limit', 0)

    html_content = f"""
    <html>
    <head>
        <title>{t('app_title')} Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .result-box {{ border: 1px solid #ccc; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
            .plot-box {{ margin-top: 20px; text-align: center; margin-bottom: 20px; }}
            img {{ max-width: 100%; border: 1px solid #ddd; }}
            .safe {{ color: green; font-weight: bold; }}
            .unsafe {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>{t('app_title')} - Report</h1>

        <div class="result-box">
            <h2>{t('results')}</h2>
            <p><strong>{t('resistance')}:</strong> {results.get('resistance', '-')} Ohm</p>
            <p><strong>{t('gpr')}:</strong> {results.get('gpr', '-')} V</p>
            <hr>
            <h3>{t('safety_limits')}</h3>
            <p><strong>{t('e_touch_limit')}:</strong> {touch_limit} V</p>
            <p><strong>{t('e_step_limit')}:</strong> {step_limit} V</p>
        </div>

        <div class="plot-box">
            <h3>{t('plot_surface')}</h3>
            <img src="data:image/png;base64,{img1}" />
        </div>

        <div class="plot-box">
            <h3>{t('plot_touch')}</h3>
            <img src="data:image/png;base64,{img2}" />
        </div>

        <div class="plot-box">
            <h3>{t('plot_step')}</h3>
            <img src="data:image/png;base64,{img3}" />
        </div>
    </body>
    </html>
    """

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        messagebox.showinfo(t('export'), f"{t('report_saved')} {filepath}")
    except Exception as e:
        messagebox.showerror(t('error'), str(e))

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return data
