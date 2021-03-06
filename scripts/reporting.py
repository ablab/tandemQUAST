import base64
from os.path import join
from collections import Counter, defaultdict

import matplotlib
import numpy as np
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from config import NUM_XTICKS

pdf_content = []

def make_plot(plot_fname, plot_type, plot_title, xlabel, ylabel, list_vals=None, legend=None,
              bar_values=None, plot_values=None, plot_color=None,
              fill_values=None, fill_color=None, fill_values2=None, fill_color2=None,
              ymax=None, max_x=None, bg_bars=None):
    fig, ax = plt.subplots(figsize=(20, 10))
    max_plot_x = 0
    if list_vals:
        list_plots = []
        bottom_vals = np.zeros(len(list_vals[0]))
        max_plot_x = max(max_plot_x, len(list_vals[0]))
        for i, v in enumerate(list_vals):
            p = ax.bar(range(len(v)), v, bottom=bottom_vals, align='edge')
            list_plots.append(p)
            bottom_vals += np.array(v)
        if legend:
            ax.legend([p[0] for p in list_plots], legend, prop={'size': 32})
    if not (bar_values is None):
        ax.bar(range(len(bar_values)), bar_values, color=plot_color, align='edge')
        max_plot_x = max(max_plot_x, len(bar_values))
    if not (plot_values is None):
        ax.plot(range(len(plot_values)), plot_values, color=plot_color)
        max_plot_x = max(max_plot_x, len(plot_values))
    if not (fill_values is None):
        ax.fill_between(range(len(fill_values)), fill_values, step="mid", color=fill_color)
        max_plot_x = max(max_plot_x, len(fill_values))
    if not (fill_values2 is None):
        ax.fill_between(range(len(fill_values2)), fill_values2, step="mid", color=fill_color2)
        max_plot_x = max(max_plot_x, len(fill_values2))

    if bg_bars:
        for b in bg_bars:
            ax.axvspan(b[0], b[1], facecolor='gray', alpha=0.1)

    plt.title(plot_title, fontsize=48)
    plt.xlabel(xlabel, fontsize=36)
    plt.ylabel(ylabel, fontsize=36)

    plt.xticks(fontsize=36)
    plt.yticks(fontsize=36)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    if max_x:
        l = matplotlib.ticker.AutoLocator()
        l.create_dummy_axis()
        xticks = [int(t) for t in l.tick_values(0, max_x)]
        if len(xticks) > NUM_XTICKS:
            xticks = [t for i,t in enumerate(xticks) if i%2==0]
        step = (xticks[1] - xticks[0]) * (max_plot_x - 1) * 1.0 / max_x
        tick_locs = [i * step for i in range(len(xticks))]
        plt.xticks(tick_locs[:-1], xticks[:-1])
    if ymax:
        plt.ylim(0, ymax)
    fig.savefig(plot_fname, bbox_inches='tight')
    pdf_content.append(fig)
    print("  %s plot is saved to %s" % (plot_type, plot_fname))
    return plot_fname


def make_plotly_noise(assemblies, all_data, out_dir):
    fig = make_subplots(rows=len(all_data), cols=1,
                        subplot_titles=[a.label for a in assemblies])
    colors = px.colors.qualitative.Plotly + px.colors.qualitative.Antique
    step = 100
    for plot_idx, (errors, coverage) in enumerate(all_data):
        customdata = []
        data = dict()
        data['coverage'] = coverage
        data['coverage'] = [max(data['coverage'][i:i+step]) for i in range(0, len(data['coverage']), step)]
        data['reads'] = [0] * len(data['coverage'])
        data['stddev'] = [0] * len(data['coverage'])
        data['diff'] = [[] for i in range(len(data['coverage']))]
        vals = [0] * len(data['coverage'])
        reads = [0] * len(data['coverage'])
        for e in errors:
            for i in range(e[0], e[1], step):
                real_pos = i #- points[k][0]
                real_pos = int(real_pos / step)
                if real_pos >= len(data['reads']):
                    break
                data['reads'][real_pos] += 1
                data['diff'][real_pos].append((e[2], e[3]))
        new_errors =[]
        for i in range(len(data['reads'])):
            diff_arr = [d[1] for d in data['diff'][i]]
            mean_diff = np.mean(diff_arr) if diff_arr else 0
            stddev = np.std(diff_arr) if diff_arr else 0
            if stddev > 200:
                stddev = min(stddev, 500)
                filt_reads = [d[0] for d in data['diff'][i] if abs(d[1]-mean_diff) <= min(mean_diff/2, 3*stddev)]
                filt_diff = [d[1] for d in data['diff'][i] if abs(d[1]-mean_diff) <= min(mean_diff/2, 3*stddev)]
            else:
                filt_diff = diff_arr
                filt_reads = [d[0] for d in data['diff'][i]]
            reads[i] = filt_reads
            mean_diff2 = np.mean(filt_diff) if filt_diff else 0
            stddev2 = np.std(filt_diff) if filt_diff else 0
            vals[i] = len(filt_reads)*1.0/(data['coverage'][i]+data['reads'][i]) if (data['coverage'][i]+data['reads'][i])>3 and len(filt_reads) > 1 else 0
            customdata.append((len(filt_reads), data['coverage'][i]+data['reads'][i], mean_diff2, stddev2))
            if vals[i]>0.5:
                new_errors.append((i*step, len(filt_reads), data['coverage'][i], data['coverage'][i]+data['reads'][i], mean_diff2, stddev2))

        plot_idx += 1
        real_x = [i*step for i in range(len(coverage))]
        fig.add_trace(
            go.Scatter(x=real_x, y=vals, showlegend=False, customdata = customdata,
                       hovertemplate="%{customdata[0]} out of %{customdata[1]} reads, "
                                     "mean diff %{customdata[2]:.2f} std deviation %{customdata[3]:.2f}"), row=plot_idx, col=1)
        fig.update_yaxes(range=[-0.05,1.05],title_text="% deviated reads", titlefont=dict(size=18), tickfont=dict(size=18),
                         hoverformat="d", row=plot_idx, col=1)
        fig.update_xaxes(title_text="Position", titlefont=dict(size=18), tickfont=dict(size=18), hoverformat="d",
                         row=plot_idx, col=1)
    bed_fname = join(out_dir, "report", "kmers_dist_diff.bed")
    prev_i = 0
    with open(bed_fname, "w") as f:
        for x,v in zip(real_x,vals):
            if v >=0.8:
                if not prev_i:
                    prev_i = x
            elif prev_i:
                f.write("seq\t%d\t%d\n" % (prev_i, x-step))
                prev_i = 0
    reads_fname = join(out_dir, "report", "reads_dist_diff.txt")
    with open(reads_fname, "w") as f:
        support_reads = set()
        for x,v,reads in zip(real_x,vals,reads):
            if v >=0.8:
                if not prev_i:
                    prev_i = x
                for r in reads:
                    support_reads.add(r)
            elif prev_i:
                f.write("seq\t%d\t%d\n" % (prev_i, x-step))
                for r in support_reads:
                    f.write(r + "\n")
                prev_i = 0
                support_reads = set()
    plot_fname = join(out_dir, "report", "kmers_dist_diff.html")
    fig.write_html(plot_fname)
    print("  Difference in k-mer distances plot saved to %s" % plot_fname)


def make_plotly_html(assembly, ref_stats, out_dir):
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=("Monomer length distribution", "Monomer lengths along the assembly"))
    colors = px.colors.qualitative.Plotly + px.colors.qualitative.Antique
    for i, monomer_name in enumerate(sorted(ref_stats.keys())):
        monomers = ref_stats[monomer_name]
        c = Counter([m[1] for m in monomers])
        monomer_lens = sorted(c.keys())
        monomer_lens.insert(0, min(monomer_lens)-1)
        monomer_lens.append(max(monomer_lens)+1)
        fig.add_trace(go.Scatter(x=monomer_lens, y=[c[v] for v in monomer_lens], mode='lines', name=monomer_name,
                                 legendgroup=monomer_name,
                                 textfont=dict(size=20), line=dict(color=colors[i % len(colors)]),
                                 hovertemplate="Monomer " + monomer_name + ", length: %{x} bp, count: %{y}"), row=1,
                      col=1)
        fig.add_trace(
            go.Scatter(x=[m[0] for m in monomers], y=[m[1] for m in monomers], mode='lines', name=monomer_name,
                       legendgroup=monomer_name,
                       textfont=dict(size=20), line=dict(color=colors[i % len(colors)]), showlegend=False,
                       hovertemplate="Monomer " + monomer_name + ", position: %{x} bp, length: %{y} bp"), row=2, col=1)
    fig.update_yaxes(title_text="Count", titlefont=dict(size=18), tickfont=dict(size=18), hoverformat="d", row=1, col=1)
    fig.update_yaxes(title_text="Length", titlefont=dict(size=18), tickfont=dict(size=18), hoverformat="d", row=2,
                     col=1)
    fig.update_xaxes(title_text="Length", titlefont=dict(size=18), tickfont=dict(size=18), hoverformat="d", row=1,
                     col=1)
    fig.update_xaxes(title_text="Position", titlefont=dict(size=18), tickfont=dict(size=18), hoverformat="d", row=2,
                     col=1)
    fig.update_layout(
        title=go.layout.Title(
            text=assembly.label,
            x=0.5,
            font=dict(size=40)
        )
    )

    plot_fname = join(out_dir, "report", assembly.name + "_monomer_lengths.html")
    fig.write_html(plot_fname)
    print("  Monomer length distribution plot saved to %s" % plot_fname)
    return fig.to_html()


def draw_report_table(report_name, extra_info, table):
    if len(table) <= 1:
        return

    column_widths = [0] * len(table[0])
    for row in table:
        for i, cell in enumerate(row):
            column_widths[i] = max(column_widths[i], len(cell))

    font_size = 12.0
    font_scale = 2.0
    external_font_scale = 10.0
    letter_height_coeff = 0.10
    letter_width_coeff = 0.04

    row_height = letter_height_coeff * font_scale
    nrows = len(table)
    external_text_height = float(font["size"] * letter_height_coeff * external_font_scale) / font_size
    total_height = nrows * row_height + 2 * external_text_height
    total_width = letter_width_coeff * font_scale * sum(column_widths)

    figure = plt.figure(figsize=(total_width, total_height))
    plt.rc('font', **font)
    plt.axis('off')
    plt.text(0.5 - float(column_widths[0]) / (2 * sum(column_widths)),
                           1. - float(2 * row_height) / total_height, report_name.replace('_', ' ').capitalize())
    plt.text(0 - float(column_widths[0]) / (2 * sum(column_widths)), 0, extra_info)
    colLabels=table[0][1:]
    rowLabels=[item[0] for item in table[1:]]
    restValues=[item[1:] for item in table[1:]]
    plt.table(cellText=restValues, rowLabels=rowLabels, colLabels=colLabels,
        colWidths=[float(column_width) / sum(column_widths) for column_width in column_widths[1:]],
        rowLoc='left', colLoc='center', cellLoc='right', loc='center')
    pdf_content.append(figure)
    plt.close()


def make_full_report(assemblies, out_dir):
    report_fname = join(out_dir, "report.pdf")
    try:
        from matplotlib.backends.backend_pdf import PdfPages
        report_file = PdfPages(report_fname)
    except:
        print('PDF report cannot be created!')
        return
    #for label, content in pdf_content.items():

    for figure in pdf_content:
        report_file.savefig(figure, bbox_inches='tight')

    report_file.close()
    plt.close('all')  # closing all open figures
    return
