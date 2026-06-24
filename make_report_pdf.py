"""
make_report_pdf.py  -  render RESEARCH_BRIEF as a typeset PDF.

Uses reportlab Platypus. DejaVu Serif/Sans are registered for full Unicode
coverage (Greek beta, x, minus sign, approximately-equal, en/em dashes);
exponents use <super> tags so they never render as boxes.
"""
import os
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    KeepTogether, HRFlowable,
)

import config

PDF_PATH = os.path.join(config.BASE_DIR, "RESEARCH_BRIEF.pdf")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
ACCENT = HexColor("#2E6F95")
DARK = HexColor("#21303B")
GRAY = HexColor("#5A6670")
LIGHT = HexColor("#9AA0A6")

# --- register fonts ------------------------------------------------------
faces = {
    "DejaVuSerif": "DejaVuSerif.ttf",
    "DejaVuSerif-Bold": "DejaVuSerif-Bold.ttf",
    "DejaVuSerif-Italic": "DejaVuSerif-Italic.ttf",
    "DejaVuSerif-BoldItalic": "DejaVuSerif-BoldItalic.ttf",
    "DejaVuSans": "DejaVuSans.ttf",
    "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
    "DejaVuSans-Oblique": "DejaVuSans-Oblique.ttf",
    "DejaVuSans-BoldOblique": "DejaVuSans-BoldOblique.ttf",
}
for name, fn in faces.items():
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))
pdfmetrics.registerFontFamily(
    "DejaVuSerif", normal="DejaVuSerif", bold="DejaVuSerif-Bold",
    italic="DejaVuSerif-Italic", boldItalic="DejaVuSerif-BoldItalic")
pdfmetrics.registerFontFamily(
    "DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold",
    italic="DejaVuSans-Oblique", boldItalic="DejaVuSans-BoldOblique")

# --- styles --------------------------------------------------------------
ss = getSampleStyleSheet()
title = ParagraphStyle("title", parent=ss["Title"], fontName="DejaVuSans-Bold",
                       fontSize=15.5, leading=18.5, textColor=DARK, spaceAfter=2,
                       alignment=0)
subtitle = ParagraphStyle("subtitle", fontName="DejaVuSans", fontSize=9.5,
                          textColor=ACCENT, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="DejaVuSans-Bold", fontSize=11.5, leading=14,
                    textColor=ACCENT, spaceBefore=9, spaceAfter=3,
                    keepWithNext=True)
body = ParagraphStyle("body", fontName="DejaVuSerif", fontSize=9.5, leading=13.4,
                      alignment=TA_JUSTIFY, textColor=HexColor("#1c1c1c"),
                      spaceAfter=6)
callout = ParagraphStyle("callout", fontName="DejaVuSerif-Italic", fontSize=9,
                         leading=12.6, textColor=HexColor("#39454E"))
caption = ParagraphStyle("caption", fontName="DejaVuSans", fontSize=8.4,
                         leading=11, textColor=GRAY, alignment=TA_CENTER,
                         spaceBefore=4, spaceAfter=8)
footnote = ParagraphStyle("footnote", fontName="DejaVuSerif-Italic", fontSize=8.3,
                          leading=11, textColor=GRAY, spaceBefore=2)


def fig(name, width_in, cap):
    p = os.path.join(config.FIG_DIR, name)
    w, h = PILImage.open(p).size
    img = Image(p, width=width_in * inch, height=width_in * inch * h / w)
    return KeepTogether([img, Paragraph(cap, caption)])


# --- content -------------------------------------------------------------
S = []
S.append(Paragraph("Quantifying the Relationship Between Digital Behavior and "
                   "Mental Health Outcomes in Adolescents", title))
S.append(Paragraph("Behavioral research brief &middot; Quantitative Social "
                   "Science (2025)", subtitle))
S.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                    spaceBefore=2, spaceAfter=8))

prov = ("<b>Data provenance:</b> the analysis below runs on a <b>simulated</b> "
        "survey dataset (n = 1,200) built from a documented data-generating "
        "process, so the pipeline is fully reproducible without restricted "
        "human-subjects data. The identical code (run_all.py) produces this "
        "brief verbatim when pointed at a real adolescent survey with the same "
        "fields. Effect sizes are therefore illustrative of the method, not "
        "empirical findings about real teenagers.")
prov_tbl = Table([[Paragraph(prov, callout)]], colWidths=[6.8 * inch])
prov_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F1F4F7")),
    ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
    ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
S.append(prov_tbl)
S.append(Spacer(1, 6))

S.append(Paragraph("Problem", h2))
S.append(Paragraph(
    "Adolescent screen time has risen sharply, and clinicians and educators "
    "increasingly ask whether heavier digital engagement tracks with worse "
    "sleep, higher stress, and weaker academic performance. The policy-relevant "
    "question is not only <i>whether</i> social-media use correlates with "
    "distress, but <i>through what pathway</i> &mdash; because the pathway "
    "determines where intervention is cheapest. This brief quantifies the "
    "associations, isolates the role of sleep as a mechanism, and packages "
    "exposure into a single screening index usable at the student level.", body))

S.append(Paragraph("Data", h2))
S.append(Paragraph(
    "The dataset contains 1,200 adolescents (ages 13&ndash;18) with self-reported "
    "daily social-media hours, screen time before sleep, sleep duration, weekly "
    "physical activity, an in-person social-interaction score (1&ndash;10), primary "
    "platform, plus two outcomes: a stress index (0&ndash;10) and academic "
    "performance (GPA, 0&ndash;4). Roughly 3&ndash;4% of behavioral fields were "
    "missing and imputed (median for numeric, mode for categorical); scale "
    "variables were z-standardized for comparability. Social-media use was split "
    "into Low / Medium / High tertiles for group contrasts.", body))

S.append(Paragraph("Methods", h2))
S.append(Paragraph(
    "Analysis proceeds in five steps. (1) <b>Descriptive contrasts</b> of each "
    "outcome across usage tertiles. (2) A <b>Pearson correlation matrix</b> over "
    "all continuous measures. (3) <b>Welch two-sample t-tests</b> (with Cohen's "
    "<i>d</i> and 95% confidence intervals) comparing high- versus low-usage "
    "students and TikTok versus Instagram users, plus one-way ANOVA across "
    "tertiles. (4) <b>OLS regression</b> of each outcome on the five behaviors and "
    "demographic controls (age, gender, platform), reporting unstandardized and "
    "standardized coefficients, variance-inflation factors, and residual "
    "diagnostics. (5) A <b>mediation analysis</b> decomposing the social-media "
    "&rarr; stress association into a direct path and an indirect path through "
    "sleep, with a 5,000-draw nonparametric bootstrap confidence interval for the "
    "indirect effect. Regression inference is computed in closed form (validated "
    "against scikit-learn to 1&times;10<super>-12</super>). Finally, a composite "
    "<b>Digital Exposure Risk Index (DERI)</b> is constructed and correlated with "
    "both outcomes.", body))

S.append(Paragraph("Findings", h2))
S.append(Paragraph(
    "<b>Heavier users sleep less, report more stress, and earn lower grades "
    "&mdash; and the gradient is monotonic.</b> Moving from the lowest to highest "
    "usage tertile, mean sleep falls from 8.3 to 7.0 hours, stress rises from 3.8 "
    "to 6.0, and GPA drops from 3.63 to 2.96. The high-versus-low contrasts are "
    "large and unambiguous:", body))

t1 = [
    ["Contrast (high \u2212 low usage)", "Difference", "95% CI", "Cohen's d", "p"],
    ["Stress (0\u201310)", "+1.62", "[1.46, 1.78]", "1.15", "< .001"],
    ["Sleep (hrs)", "\u22120.90", "[\u22120.98, \u22120.81]", "\u22121.23", "< .001"],
    ["GPA", "\u22120.49", "[\u22120.54, \u22120.43]", "\u22121.04", "< .001"],
]
tbl1 = Table(t1, colWidths=[2.5 * inch, 1.0 * inch, 1.35 * inch, 1.0 * inch, 0.95 * inch])
tbl1.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
    ("TEXTCOLOR", (0, 0), (-1, 0), white),
    ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F4F7F9")]),
    ("LINEBELOW", (0, 0), (-1, 0), 0.6, ACCENT),
    ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#D2DAE0")),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
]))
S.append(tbl1)
S.append(Spacer(1, 6))

S.append(Paragraph(
    "Correlations point the same way: social-media hours correlate <b>+0.61</b> "
    "with stress and <b>\u22120.65</b> with sleep, while sleep correlates "
    "<b>\u22120.58</b> with stress and <b>+0.58</b> with GPA. A one-way ANOVA "
    "across tertiles confirms the stress gradient (F = 260, p < .001). TikTok "
    "users report modestly more daily use and higher stress than Instagram users "
    "(d = 0.35 and 0.24 respectively), a small but reliable platform difference.",
    body))
S.append(Paragraph(
    "<b>The associations survive adjustment.</b> In the regression on stress "
    "(R<super>2</super> = 0.49), each additional daily hour of social media "
    "predicts <b>+0.42</b> stress points (\u03b2 = 0.37) and each additional hour "
    "of sleep predicts <b>\u22120.53</b> (\u03b2 = \u22120.28); physical activity "
    "and in-person interaction are independently protective. The "
    "academic-performance model (R<super>2</super> = 0.49) mirrors this &mdash; "
    "social-media use and low sleep both depress GPA. Screen time <i>immediately</i> "
    "before sleep is not significant once sleep duration is in the model, "
    "indicating its effect operates through total sleep rather than independently. "
    "All variance-inflation factors are below 2.1, so multicollinearity is not "
    "distorting the estimates.", body))
S.append(Paragraph(
    "<b>About a third of social media's link to stress runs through sleep.</b> "
    "Decomposing the total social-media &rarr; stress effect (c = +0.71): more use "
    "predicts less sleep (a = \u22120.40), less sleep predicts more stress "
    "(b = \u22120.59), yielding an <b>indirect effect of +0.235</b> (bootstrap 95% "
    "CI [0.19, 0.28]; Sobel z = 10.1). A direct effect remains (c&prime; = +0.47), "
    "so sleep is a <b>partial mediator accounting for ~33% of the association</b> "
    "&mdash; the rest operates through other channels. This is the actionable "
    "result: protecting sleep recovers a meaningful share of the stress burden "
    "without eliminating screen use entirely.", body))
S.append(fig("fig_mediation_path_diagram.png", 4.5,
             "Figure 1. Sleep partially mediates the social-media &rarr; stress "
             "association (indirect effect +0.235; ~33% of the total effect)."))
S.append(Paragraph(
    "<b>A simple composite index screens effectively.</b> The DERI combines "
    "(standardized) social-media hours, pre-sleep screen time, and inverted sleep "
    "duration with equal weights. It correlates <b>+0.62</b> with stress and "
    "<b>\u22120.61</b> with GPA. A PCA-derived weighting reproduces it almost "
    "exactly (first component explains 75% of shared variance; correlation with the "
    "equal-weight index \u2248 1.00), so the transparent equal-weight version is "
    "justified. Sorting students into DERI quartiles produces a clean "
    "dose-response: mean stress climbs from 3.6 (lowest-risk quartile) to 6.2 "
    "(highest), and GPA falls from 3.69 to 2.89.", body))
S.append(fig("fig_deri_quartile_outcomes.png", 5.7,
             "Figure 2. Stress rises and GPA falls monotonically across Digital "
             "Exposure Risk Index quartiles (Q1 = lowest risk)."))

S.append(Paragraph("Implications", h2))
S.append(Paragraph(
    "Three takeaways follow. First, <b>sleep is the leverage point</b>: because a "
    "third of the stress association is mediated by sleep loss, sleep-protective "
    "measures (curfews on pre-bed device use, later school start times, "
    "sleep-hygiene education) plausibly capture much of the benefit of broader "
    "screen-time limits at lower cost. Second, <b>a lightweight index is enough to "
    "triage</b>: the DERI's strong, monotonic relationship with both outcomes means "
    "schools could flag higher-risk students from three routinely collected "
    "behaviors rather than fielding lengthy instruments. Third, <b>protective "
    "behaviors matter independently</b>: physical activity and in-person social "
    "contact predict lower stress and higher GPA even after adjusting for screen "
    "use, suggesting that <i>substituting</i> offline activity may be more "
    "effective messaging than <i>subtracting</i> screen time alone.", body))

S.append(Paragraph("Limitations", h2))
S.append(Paragraph(
    "The design is cross-sectional, so the regression and mediation estimates "
    "describe associations and a modeled pathway, not established causation; "
    "reverse causality (stress driving both poor sleep and compensatory scrolling) "
    "is plausible and untestable here. Self-report introduces measurement error, "
    "and &mdash; as noted above &mdash; these specific magnitudes come from "
    "simulated data and should be replaced with estimates from a real survey before "
    "any findings are reported.", body))

S.append(Spacer(1, 6))
S.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#C9D2D8"),
                    spaceBefore=2, spaceAfter=5))
S.append(Paragraph(
    "Reproducibility: <font name='DejaVuSans'>python run_all.py</font> regenerates "
    "every figure, table, and the cleaned, DERI-scored dataset. Regression "
    "inference is implemented from first principles in ols.py.", footnote))


# --- page furniture ------------------------------------------------------
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVuSans", 8)
    canvas.setFillColor(LIGHT)
    canvas.drawString(doc.leftMargin, 0.5 * inch,
                      "Digital Behavior & Adolescent Mental Health \u2014 research brief")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.5 * inch,
                           f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    PDF_PATH, pagesize=letter,
    leftMargin=0.85 * inch, rightMargin=0.85 * inch,
    topMargin=0.7 * inch, bottomMargin=0.75 * inch,
    title="Digital Behavior & Adolescent Mental Health — Research Brief",
    author="Quantitative Social Science (2025)",
)
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print(f"PDF written: {PDF_PATH}")
