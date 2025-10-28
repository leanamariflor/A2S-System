# Degree Audit Page - A2S Next-Gen: Academic To Success

## Overview

This document describes the implementation of a fully dynamic Degree Audit page for the A2S Student Dashboard System. The page provides comprehensive academic progress tracking, course management, GPA calculation, and personalized recommendations.

## Features Implemented

### ✅ 1. Dynamic Student Data Retrieval
- **Model Used**: `StudentProfile` from `students.models`
- **Fields Retrieved**:
  - `user` - Current logged-in user
  - `program` - Student's academic program
  - `year_level` - Current year (1-4)
  - `credits_completed` - Total units earned
  - `credits_required` - Total units needed for graduation
  - `gpa` - Current GPA
  - `expected_graduation` - Target graduation date

### ✅ 2. Course Categorization
Courses are automatically categorized into:

#### General Education
- Identified by prefixes: `GE`, `ENGL`, `MATH`, `PHILO`, `HUM`, `SOCSCI`, `NATSCI`, `HIST`, `PSYCH`, `PE`, `NSTP`

#### Major Core Courses
- Identified by prefixes: `IT`, `CSIT`, `CS`

#### Electives
- Identified by keywords: `ELEC`, `ELCE`, `FREEEL`

#### Minor/Specialization
- All other courses not matching above categories

### ✅ 3. Course Information Display
Each course card shows:
- **Course Code** (e.g., IT317)
- **Course Title** (e.g., Project Management I)
- **Units/Credits** (e.g., 3 units)
- **Status Badge**:
  - ✅ **Completed** (PASSED) - Green
  - ⏳ **In Progress** (CURRENT) - Yellow
  - ⭕ **Not Started** (RECOMMENDED) - Blue
- **Semester/Term** (e.g., Third Year - First Term)

### ✅ 4. Progress Calculations

#### Completion Percentage
```python
completion_percentage = (completed_units / total_units) * 100
```

#### Credits Remaining
```python
credits_remaining = total_units - completed_units
```

#### Current GPA
- Retrieved directly from `StudentProfile.gpa`

### ✅ 5. Visual Progress Circle
- **Animated SVG circle** showing completion percentage
- **Gradient color scheme**: Blue to Purple
- **Smooth animation** on page load
- **Responsive design** for mobile devices

### ✅ 6. What-If Grade Calculator

#### Functionality
Users can predict their GPA by:
1. Selecting a course (in progress or not started)
2. Choosing an expected grade (1.00 - 5.00)
3. Clicking "Calculate"

#### Calculation Formula
```javascript
currentGradePoints = currentGPA × currentUnits
newGradePoints = expectedGrade × courseUnits
newTotalUnits = currentUnits + courseUnits
predictedGPA = (currentGradePoints + newGradePoints) / newTotalUnits
```

#### Output
- **Predicted GPA** (e.g., 2.35)
- **Change Indicator**:
  - ↑ +0.15 improvement (green)
  - ↓ -0.10 decrease (red)
  - — No change (gray)

### ✅ 7. Achievements Display
- Fetches achievements from `Achievement` model
- Each achievement shows:
  - Icon (from Lucide icons library)
  - Title
  - Description
- **Dynamic**: Updates when logged-in student changes

### ✅ 8. Recommended Courses
**Selection Criteria**:
1. Courses with status `RECOMMENDED`
2. Based on student's current `year_level`
3. Shows next semester's courses
4. Limited to top 6 recommendations

**Display Information**:
- Course code and title
- Units
- Semester/term

### ✅ 9. Action Buttons
Three quick-access buttons:
- 🏠 **View Roadmap** → Links to `StudentDashboard`
- 📅 **View Schedule** → Links to `StudentSchedule`
- 📋 **View Grades** → Links to `StudentGrades`

## Files Created/Modified

### 1. Backend View
**File**: `c:\Users\JAYLORD\OneDrive\Desktop\A2S-System-1\a2s\students\views.py`

Added `student_degree_audit` view function:
- Retrieves student profile
- Loads curriculum from database
- Categorizes courses
- Calculates progress metrics
- Fetches achievements
- Generates course recommendations
- Passes all data to template

### 2. HTML Template
**File**: `c:\Users\JAYLORD\OneDrive\Desktop\A2S-System-1\a2s\a2s\templates\students\StudentDegreeAudit.html`

**Sections**:
- Page Header with program and semester badges
- Progress Overview with animated circle
- Quick Stats (Completed, In Progress, Remaining)
- Course Categories with tab navigation
- What-If Grade Calculator
- Achievements section
- Recommended Courses for next semester
- Action buttons for navigation

### 3. CSS Styling
**File**: `c:\Users\JAYLORD\OneDrive\Desktop\A2S-System-1\a2s\a2s\static\students\css\student_degree_audit.css`

**Features**:
- Modern color scheme with CSS variables
- Responsive grid layouts
- Card-based design
- Smooth animations and transitions
- Mobile-first approach
- Hover effects and interactions
- Progress circle styling

### 4. JavaScript
**File**: `c:\Users\JAYLORD\OneDrive\Desktop\A2S-System-1\a2s\a2s\static\students\js\student_degree_audit.js`

**Functions**:
- `initializeTabs()` - Tab switching for course categories
- `animateProgressCircle()` - Animated completion percentage
- `initializeCalculator()` - What-If calculator logic
- `calculatePredictedGPA()` - GPA prediction algorithm
- `displayCalculatorResult()` - Show results with animation

### 5. URL Routing
**File**: `c:\Users\JAYLORD\OneDrive\Desktop\A2S-System-1\a2s\students\urls.py`

Added route:
```python
path('StudentDegreeAudit/', views.student_degree_audit, name='StudentDegreeAudit')
```

### 6. Navigation Update
**File**: `c:\Users\JAYLORD\OneDrive\Desktop\A2S-System-1\a2s\a2s\templates\students\student_base.html`

Updated sidebar navigation to include clickable link to Degree Audit page.

## Dynamic Behavior

### Per-Student Customization
✅ **All data updates automatically** when different students log in:

1. **Progress metrics** recalculated based on student's completed units
2. **Course lists** filtered by student's program curriculum
3. **GPA** retrieved from student's profile
4. **Achievements** fetched from student's achievement records
5. **Recommendations** generated based on student's year level

### Real-time Updates
The page fetches data from:
- `StudentProfile` model → Personal information
- `Curriculum` model → Program courses
- `Achievement` model → Student achievements
- Academic calendar JSON → Current semester info

## Usage

### Accessing the Page
1. Log in as a student
2. Navigate to sidebar
3. Click "Degree Audit" button
4. Page loads with your personalized data

### Using What-If Calculator
1. Scroll to "What-If Grade Calculator" section
2. Select a course from dropdown
3. Choose expected grade (1.00 - 5.00)
4. Click "Calculate" button
5. View predicted GPA and change indicator

### Viewing Course Categories
1. Use tab buttons to switch between:
   - General Education
   - Major Core
   - Electives
   - Minor/Specialization
2. Each course shows status with color coding
3. Hover over cards for visual feedback

## Technical Details

### Technologies Used
- **Backend**: Django Python
- **Frontend**: HTML5, CSS3, JavaScript
- **Icons**: Lucide Icons
- **Database**: Django ORM with PostgreSQL/SQLite

### Browser Compatibility
- ✅ Chrome (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)
- ✅ Edge (Latest)

### Responsive Breakpoints
- **Desktop**: 1024px and above
- **Tablet**: 768px - 1023px
- **Mobile**: Below 768px

## Future Enhancements (Potential)

1. **PDF Export** - Download degree audit as PDF
2. **Course Prerequisites** - Show prerequisite chains
3. **Progress Timeline** - Visual timeline of completed semesters
4. **Grade Trends** - Chart showing GPA over time
5. **Degree Requirement Checklist** - Interactive checklist
6. **Course Comparison** - Compare course options
7. **Academic Advisor Notes** - Comments from advisors

## Testing Checklist

- [x] Page loads without errors
- [x] Student data displays correctly
- [x] Course categorization works
- [x] Progress circle animates
- [x] What-If calculator calculates correctly
- [x] Tabs switch properly
- [x] Achievements display (when available)
- [x] Recommended courses show
- [x] Navigation buttons work
- [x] Responsive on mobile devices
- [x] Works for different logged-in students

## Support

For issues or questions, contact the A2S development team.

---

**Version**: 1.0.0  
**Last Updated**: October 28, 2025  
**Author**: A2S Development Team
