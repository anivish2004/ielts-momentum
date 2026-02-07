IELTS Momentum
An engagement & gamification solution for IELTS preparation.

What's This About?
Look, everyone knows IELTS prep is boring. You grind for weeks, and nothing feels like progress until you take a full mock test. By then, half your students have already quit.

IELTS Momentum fixes that. It's a micro-learning platform that turns a painful 3-month marathon into something actually doable—bite-sized 5-minute daily tasks that feel rewarding. Think Duolingo, but for IELTS.

We built it as a Streamlit app with MongoDB backend. It's live, tested, and ready to go.

The Problem We're Solving
Why Students Quit IELTS Prep
I spent time talking to IELTS students, and the pattern was clear:

Week 1-2: They're excited. Buying courses, making study plans.

Week 3-4: Motivation crashes. They've done practice passages, mock tests feel far away. No visible win.

Week 5+: They only care when the exam date is 2 weeks away.

The numbers back this up. Standard EdTech platforms lose 92% of users by Day 30. Only 8-15% of students actually finish the course.

Compare that to Duolingo—they keep 55% of users by Day 1, and maintain 92% retention on users with 30-day streaks. Why? Because they made daily practice feel like a game, not a grind.

How We Fixed It
Instead of asking students to commit 2 hours daily, we said: "Just 5 minutes. Today."

We built four key mechanics:

1. Daily Tasks
Every morning, 3 new tasks appear (Easy, Medium, Hard). Reading passage. Listening snippet. Writing prompt. Pick one, spend 5-12 minutes, move on. Done.

Each task gives you XP:

Easy task = 10 XP

Medium task = 20 XP

Hard task = 30 XP

2. Levels That Mean Something
Every 100 XP = 1 Level = roughly 1 hour of actual study time. Your level tells you exactly how many hours you've invested. Level 10? You've studied 10 hours. Level 50? 50 hours.

It's transparent. You can see your progress in real numbers, not vague percentages.

3. Streaks (The Secret Sauce)
A fire counter (🔥) shows your consecutive days. Miss one day? It resets to 0.

That hurts more than you'd think. After 7 days, you don't want to break the chain. After 30 days, you can't break it. Duolingo's research shows:

10-day streak = 75% chance you keep going

30-day streak = 92% won't quit

We use the exact same psychology.

4. One Dashboard
All four skills (Listening, Reading, Writing, Speaking) tracked in one place. You see trends, weak spots, progress over time. Not isolated practice sessions—a unified picture of where you stand.

Getting Started
What You Need
Python 3.8+

MongoDB (free account on MongoDB Atlas)

Git (if you want to clone and run locally)

Quick Setup
bash
# Clone the repo
git clone https://github.com/anivish2004/ielts-momentum.git
cd ielts-momentum

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Then create a .streamlit/secrets.toml file with your MongoDB credentials:

text
[mongo]
uri = "your_mongodb_connection_string_here"
db_name = "ielts_momentum"
Fire it up:

bash
streamlit run app.py
You'll see it running at http://localhost:8501

Try the Live Version
Don't want to set up locally? [Go here](https://ielts-momentum.streamlit.app/)

Test it out:

Student account: demo / demo123

Admin account: admin / leap123

Just poke around, complete some tasks, check the leaderboard. Get a feel for it.

What's Actually In Here
For Students
A dashboard showing your level, XP, streak, and target band score

Daily practice tasks personalized to your weak areas

A graph tracking your score progress in each skill

Leaderboard (because who doesn't like friendly competition?)

Settings to log your mock test scores and update your target

For Admins
A metrics dashboard showing how many users are active, how many completed tasks, engagement trends

User management (create new users, promote/demote, delete if needed)

Content editor to add new daily challenges

How We Measure Success
We're targeting these metrics over the first 4 weeks:

What We're Measuring	Our Target	Industry Average	Why It Matters
Users still active on Day 30	30-35%	8-10%	If people stick around, they actually prepare
Tasks completed per user per month	12-15	4-6	More practice = better scores
Average time per session	8-12 min	2:51	Shows our micro-learning works
Course completion rate	40-50%	8-15%	Most students actually finish
These numbers aren't made up. They come from GetStream's 2026 app retention study, Duolingo case studies, and NCBI research on spaced repetition. We're being realistic but ambitious.

The Stack
Frontend: Streamlit (Python, minimal learning curve)

Database: MongoDB (Cloud, scales well, flexible schema)

Auth: Bcrypt for password hashing (not storing anything in plain text)

Sessions: Extra Streamlit Components for 7-day cookies

Graphs: Plotly (pretty visualizations)

Hosting: Streamlit Cloud (free tier works, scales if needed)

How the Daily Loop Actually Works
Here's what a user sees:

Morning: Notification pops up. "Good morning! 3 quick tasks ready. Keep your 🔥 streak alive? Complete one in 5 mins."

User's Turn: Logs in, picks a task (e.g., "Reading - Medium - 8 mins"). Does the practice. Enters their score.

Instant Reward: Confetti animation. "+20 XP" pops up. Streak increments. Level progress bar fills a bit more.

Weekly: Friday evening, they check the leaderboard. Sees they're Top 10. Feels good. Unlocks a badge. Motivation to keep going.

That's it. Simple loop. Repeats daily. Habits form.

What's Actually Happening Behind the Scenes
The app does a few important things:

Generates daily tasks based on what you're weak at

Tracks everything in MongoDB (XP, streaks, scores, activity)

Calculates levels using proper IELTS band score rounding (the official way)

Shows real-time progress without page refreshes

Keeps you logged in for 7 days with secure cookies

The Research We're Standing On
We didn't just guess at these ideas. Everything's based on actual studies:

Duolingo Case Study: Their 55% Day-1 retention comes from streaks. We're using the exact same psychology.

NCBI Study: Spaced repetition (daily 5-min tasks) is 30-40% more efficient than weekly 2-hour cramming sessions.

GetStream 2026: EdTech retention benchmarks. Standard apps lose 92% by Day 30.

BabyCode Analysis: Top IELTS app. They report +1.5 band improvement in 6 weeks. We're targeting +0.3-0.5 in 4 weeks, which is proportionally aligned.

ERIC Study: Online course completion rates. 2-18% is typical. We're targeting 40-50% with gamification.

What We're Building Next
LeapScholar API integration: Pull mock test scores directly from their database (no manual entry)

Mobile app: React Native so students can practice on the go

AI recommendations: Algorithm to suggest which skills to focus on

Push notifications: Email/SMS reminders so students don't forget

Social challenges: Friend competitions, team mode

Export reports: For parents/teachers to see progress

Offline mode: Download tasks, practice without internet

Security 
Passwords are hashed with bcrypt. We're not storing passwords in plain text.

Sessions are secure cookies that expire after 7 days.

MongoDB credentials are in secrets.toml which is .gitignored (not on GitHub).

Admin routes are protected. Regular users can't access them.

Each user only sees their own data.

It's not Fort Knox, but it's solid for an MVP.

The Mission
IELTS prep shouldn't feel like punishment. It should feel like progress. Like winning.

We built something that makes daily practice feel rewarding, streaks feel important, and progress feel real.

Try it. See if it works for you.

Last Updated: January 29, 2026
Status: Live & Working ✅

Built by Animesh Vishwakarma
