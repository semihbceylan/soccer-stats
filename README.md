# Soccer Team Management and Match Tracking System

This project is a web application built with Flask for managing soccer teams, tracking matches, and viewing match statistics. It provides functionalities for team and player management, real-time match tracking, and visualization of match data.

---

## Features

### General
- User-friendly web interface for team and match management.
- Integration of database-backed player and team records.
- Modular design for scalability and maintainability.

### Team and Player Management
- **Add, Update, and Delete Players and Teams**: Manage teams and players in the system.
- **Image Uploads**: Upload player images with validation for common image formats.

### Match Tracking
- **Real-Time Match Events**: Log match events such as goals, fouls, and cards during a match.
- **Match Timer**: Automatic tracking of match time, including support for extensions.
- **Detailed Match Events**: View match events in tabular format for better understanding.

### Statistics
- Generate and view statistics for completed matches, including team-specific and player-specific metrics.

---

## Technologies Used

- **Frontend**: HTML, CSS (custom styling with animations), JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Deployment**: Flask development server
- **Other**: Modular templates using Jinja2, RESTful API endpoints for logging actions.

---

## Installation

### Prerequisites
- Python 3.x
- `pip` (Python package manager)

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/soccer-team-tracker.git
    cd soccer-team-tracker
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Initialize the database:
    ```bash
    python sql_queries.py
    ```

4. Run the application:
    ```bash
    python app.py
    ```

5. Access the app at `http://127.0.0.1:5000`.

---

## File Structure

### Backend
- **`app.py`**: Main Flask app with routes for team management, match tracking, and statistics.
- **`external_model.py`**: RESTful API endpoints for match tracking and player actions.
- **`pull_player_data.py`**: Script for bulk adding player and team data to the database.
- **`sql_queries.py`**: Handles database initialization and table schema definitions.

### Templates
- **`base.html`**: Base layout with a responsive navbar and footer.
- **`homepage.html`**: Homepage with navigation to features.
- **`team_management`, `match_tracking`, `match_statistics`**: Submodules for feature-specific pages.

### Static
- **`style.css`**: Custom CSS for theming and animations.
- **Player Images**: Uploaded player images stored in `static/uploads`.

---

## Usage

### 1. Manage Teams and Players
- Navigate to **Manage Your Teams** from the homepage.
- Add, update, or delete players and teams as needed.

### 2. Track a Match
- Select teams and start a new match.
- Use the match tracker to log events and view match details.

### 3. View Match Statistics
- Navigate to **Match Statistics** to see the summary of completed matches.

---

## Future Enhancements
- **Live Match Visualization**: Add charts for real-time event tracking.
- **Player Profiles**: Expand player data to include career stats and achievements.
- **Mobile Support**: Enhance responsiveness for better usability on smaller devices.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
