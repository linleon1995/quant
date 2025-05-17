import matplotlib.pyplot as plt


def draw_offset_circles(n=10, radius=1, offset=0.02):
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_aspect('equal')
    for i in range(n):
        x = i * offset
        color = plt.cm.viridis(i / n)
        circle = plt.Circle((x, 0), radius, color=color, fill=True, lw=2)
        ax.add_patch(circle)
    ax.set_xlim(-1, n * offset + radius)
    ax.set_ylim(-radius * 1.5, radius * 1.5)
    plt.axis('off')
    plt.show()

draw_offset_circles(n=20)
