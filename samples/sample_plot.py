"""
Generate sample histogram showing frequency of waypoint activity by time of day.
Highlights peak flight hours.
"""
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random

def generate_sample_plot():
    """Create histogram showing distribution of waypoint activity by hour of day."""
    random.seed(42)

    # Generate 30 days of waypoint data with times of day
    start_date = datetime(2025, 1, 1)
    hours_of_day = []

    for i in range(30):
        current_date = start_date + timedelta(days=i)
        # Random 2-8 waypoints per day
        num_waypoints = random.randint(2, 8)

        for _ in range(num_waypoints):
            # Random hour of day (0-23)
            hour = random.randint(0, 23)
            hours_of_day.append(hour)

    # Create histogram
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_facecolor('#0f1419')
    fig.patch.set_facecolor('#0a0d12')

    # Histogram with hourly bins
    n, bins, patches = ax.hist(hours_of_day, bins=24, range=(0, 24), color='#00d9ff',
                               edgecolor='#00a8cc', linewidth=1.5, alpha=0.8)

    ax.set_title('Waypoint Activity by Time of Day (Peak Hours)', fontsize=16, color='#00d9ff', weight='bold', pad=20)
    ax.set_xlabel('Hour of Day', color='#00d9ff', fontsize=12)
    ax.set_ylabel('Frequency (# of Waypoints)', color='#00d9ff', fontsize=12)

    # Set X-axis to show all hours
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(24)], rotation=45, ha='right')

    # Style axes - cyan/teal theme
    ax.tick_params(colors='#00d9ff', labelsize=9)
    ax.spines['bottom'].set_color('#00d9ff')
    ax.spines['left'].set_color('#00d9ff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)

    ax.grid(True, alpha=0.15, color='#00d9ff', linestyle='--', linewidth=0.8, axis='y')

    # Add peak indicator on the right side
    peak_idx = max(range(len(n)), key=lambda i: n[i])
    peak_hour = int(bins[peak_idx])
    peak_count = n[peak_idx]
    fig.text(0.92, 0.92, f'Peak: {peak_hour:02d}:00\n({int(peak_count)} flights)',
            ha='right', va='top', color='#00d9ff', fontsize=11, weight='bold',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#0f1419', edgecolor='#00d9ff', linewidth=1.5))

    plt.tight_layout()

    # Save and show
    plt.savefig('sample_waypoint_plot.png', dpi=150, facecolor='#0a0d12')
    print("Sample histogram saved to sample_waypoint_plot.png")
    plt.show()


if __name__ == '__main__':
    generate_sample_plot()
