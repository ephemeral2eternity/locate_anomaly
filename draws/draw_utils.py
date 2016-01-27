import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from outlier_detection import *
from read_data.load_metrics import *
from matplotlib.backends.backend_pdf import PdfPages


def plot_scatter(x, y):
    plt.scatter(x, y, alpha=0.5)
    plt.show()


def draw_cdf(data, ls, lg):
    sorted_data = sorted(data)
    yvals = np.arange(len(sorted_data))/float(len(sorted_data))
    plt.plot(yvals, sorted_data, ls, label=lg, linewidth=2.0)
# plt.show()


def save_fig(fig, figName, figFolder = "./imgs/"):
    pdf = PdfPages(figFolder + figName + '.pdf')
    pdf.savefig(fig)
    fig.savefig(figFolder + figName+'.png', dpi=600, format='png')
    pdf.close()

