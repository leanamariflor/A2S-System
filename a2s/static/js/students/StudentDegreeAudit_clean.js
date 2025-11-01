// ========================================
// Degree Audit JavaScript (Cleaned Version)
// ========================================

console.log('🎓 Degree Audit JavaScript loaded!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 DOMContentLoaded event fired!');
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
        console.log('✓ Lucide icons initialized');
    } else {
        console.warn('⚠ Lucide library not found');
    }

    // Initialize tab functionality
    initializeTabs();

    // Initialize What-If Calculator
    initializeCalculator();

    // Animate progress circle
    animateProgressCircle();
    
    console.log('✓ All initializations complete!');
});

// ========================================
// Tab Switching Functionality
// ========================================

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.category-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetCategory = button.getAttribute('data-category');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const targetContent = document.querySelector(`.category-content[data-category="${targetCategory}"]`);
            if (targetContent) {
                targetContent.classList.add('active');
            }

            // Reinitialize icons after tab switch
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        });
    });
}

// ========================================
// Progress Circle Animation
// ========================================

function animateProgressCircle() {
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;

    // Get the completion percentage from the stroke-dasharray attribute
    const strokeDasharray = progressBar.getAttribute('style');
    const match = strokeDasharray.match(/stroke-dasharray:\s*([\d.]+)/);
    
    if (match) {
        const percentage = parseFloat(match[1]);
        const circumference = 2 * Math.PI * 75; // radius = 75
        const offset = circumference - (percentage / 100) * circumference;

        // Animate the progress circle
        progressBar.style.strokeDasharray = circumference;
        progressBar.style.strokeDashoffset = circumference;

        setTimeout(() => {
            progressBar.style.transition = 'stroke-dashoffset 1.5s ease-in-out';
            progressBar.style.strokeDashoffset = offset;
        }, 100);
    }
}

// ========================================
// What-If Grade Calculator
// ========================================

function initializeCalculator() {
    const form = document.getElementById('whatIfForm');
    const courseSelect = document.getElementById('courseSelect');
    const gradeSelect = document.getElementById('gradeSelect');
    const resultDiv = document.getElementById('calculatorResult');
    const predictedGpaSpan = document.getElementById('predictedGPA');
    const gpaChangeSpan = document.getElementById('gpaChange');

    if (!form || !courseSelect || !gradeSelect) {
        console.warn('Calculator elements not found');
        return;
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const selectedCourse = courseSelect.value;
        const selectedGrade = gradeSelect.value;

        if (!selectedCourse || !selectedGrade) {
            alert('Please select both a course and a grade.');
            return;
        }

        // Find the selected course details
        const course = allCoursesData.find(c => c.code === selectedCourse);
        if (!course) {
            alert('Course not found.');
            return;
        }

        // Calculate predicted GPA
        const gradeValue = parseFloat(selectedGrade);
        const predictedGPA = calculatePredictedGPA(course, gradeValue);
        const gpaChange = predictedGPA - currentGPA;

        // Display result
        predictedGpaSpan.textContent = formatGPA(predictedGPA);
        gpaChangeSpan.textContent = (gpaChange >= 0 ? '+' : '') + formatGPA(gpaChange);
        gpaChangeSpan.className = gpaChange >= 0 ? 'positive' : 'negative';
        
        resultDiv.style.display = 'block';
        
        // Animate result
        resultDiv.style.opacity = '0';
        resultDiv.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            resultDiv.style.transition = 'all 0.3s ease';
            resultDiv.style.opacity = '1';
            resultDiv.style.transform = 'translateY(0)';
        }, 10);
    });
}

/**
 * Calculate predicted GPA with a hypothetical grade
 */
function calculatePredictedGPA(course, gradeValue) {
    const courseUnits = parseInt(course.units) || 0;
    
    // Calculate current grade points
    const currentGradePoints = currentGPA * completedUnits;
    
    // Add hypothetical course grade points
    const newGradePoints = gradeValue * courseUnits;
    const totalGradePoints = currentGradePoints + newGradePoints;
    
    // Calculate new GPA
    const newTotalUnits = completedUnits + courseUnits;
    const predictedGPA = newTotalUnits > 0 ? totalGradePoints / newTotalUnits : 0;
    
    return predictedGPA;
}

/**
 * Format GPA to 2 decimal places
 */
function formatGPA(gpa) {
    return gpa.toFixed(2);
}

/**
 * Get status color based on grade
 */
function getStatusColor(status) {
    const statusColors = {
        'COMPLETED': '#10b981',
        'IN PROGRESS': '#3b82f6',
        'NOT TAKEN': '#94a3b8',
        'FAILED': '#ef4444'
    };
    return statusColors[status.toUpperCase()] || '#94a3b8';
}

/**
 * Count courses by status
 */
function countCoursesByStatus(courses, status) {
    return courses.filter(course => 
        course.status.toUpperCase() === status.toUpperCase()
    ).length;
}

// ========================================
// Console Info
// ========================================

console.log('%c🎓 A2S Degree Audit System', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('%cDegree audit page loaded successfully', 'color: #10b981; font-size: 12px;');
