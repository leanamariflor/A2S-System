// ========================================
// Degree Audit JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Initialize tab functionality
    initializeTabs();

    // Initialize What-If Calculator
    initializeCalculator();

    // Animate progress circle
    animateProgressCircle();
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
            alert('Please select both a course and an expected grade.');
            return;
        }

        // Get course units from the selected option
        const selectedOption = courseSelect.options[courseSelect.selectedIndex];
        const courseUnits = parseInt(selectedOption.getAttribute('data-units')) || 3;

        // Calculate predicted GPA
        const result = calculatePredictedGPA(
            currentGPA,
            completedUnits,
            parseFloat(selectedGrade),
            courseUnits
        );

        // Display result
        displayCalculatorResult(result, resultDiv, predictedGpaSpan, gpaChangeSpan);
    });
}

/**
 * Calculate predicted GPA using weighted average
 * 
 * @param {number} currentGPA - Current GPA
 * @param {number} currentUnits - Total units completed
 * @param {number} expectedGrade - Expected grade for the new course (1.00 - 5.00)
 * @param {number} courseUnits - Units for the new course
 * @returns {object} - Object containing predictedGPA and change
 */
function calculatePredictedGPA(currentGPA, currentUnits, expectedGrade, courseUnits) {
    // Calculate total grade points earned so far
    const currentGradePoints = currentGPA * currentUnits;

    // Calculate grade points for the new course
    const newGradePoints = expectedGrade * courseUnits;

    // Calculate new total units
    const newTotalUnits = currentUnits + courseUnits;

    // Calculate predicted GPA
    const predictedGPA = (currentGradePoints + newGradePoints) / newTotalUnits;

    // Calculate change in GPA
    const gpaChange = predictedGPA - currentGPA;

    return {
        predictedGPA: predictedGPA,
        change: gpaChange,
        isImprovement: gpaChange > 0,
        isDecline: gpaChange < 0
    };
}

/**
 * Display calculator result with animation
 */
function displayCalculatorResult(result, resultDiv, predictedGpaSpan, gpaChangeSpan) {
    // Update predicted GPA
    predictedGpaSpan.textContent = result.predictedGPA.toFixed(2);

    // Format change message
    let changeMessage = '';
    let changeClass = '';

    if (result.change > 0) {
        changeMessage = `↑ +${result.change.toFixed(2)} improvement`;
        changeClass = 'positive';
    } else if (result.change < 0) {
        changeMessage = `↓ ${result.change.toFixed(2)} decrease`;
        changeClass = 'negative';
    } else {
        changeMessage = '— No change';
        changeClass = 'neutral';
    }

    gpaChangeSpan.textContent = changeMessage;
    gpaChangeSpan.className = `result-change ${changeClass}`;

    // Show result with animation
    resultDiv.style.display = 'block';

    // Scroll to result smoothly
    setTimeout(() => {
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// ========================================
// Course Card Interactions
// ========================================

// Add click handlers to course cards for potential future functionality
document.addEventListener('click', (e) => {
    const courseCard = e.target.closest('.course-card');
    if (courseCard) {
        // Future: Show course details modal or expand card
        // For now, just add visual feedback
        courseCard.style.transform = 'scale(0.98)';
        setTimeout(() => {
            courseCard.style.transform = '';
        }, 100);
    }
});

// ========================================
// Achievement Card Hover Effects
// ========================================

const achievementCards = document.querySelectorAll('.achievement-card');
achievementCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
        const icon = this.querySelector('.achievement-icon');
        if (icon) {
            icon.style.transform = 'rotate(10deg) scale(1.1)';
        }
    });

    card.addEventListener('mouseleave', function() {
        const icon = this.querySelector('.achievement-icon');
        if (icon) {
            icon.style.transform = '';
        }
    });
});

// ========================================
// Utility Functions
// ========================================

/**
 * Format GPA to 2 decimal places
 */
function formatGPA(gpa) {
    return parseFloat(gpa).toFixed(2);
}

/**
 * Get status badge color based on course status
 */
function getStatusColor(status) {
    const colors = {
        'PASSED': '#10b981',
        'CURRENT': '#f59e0b',
        'RECOMMENDED': '#06b6d4'
    };
    return colors[status.toUpperCase()] || '#64748b';
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
// Export for potential external use
// ========================================

window.degreeAuditUtils = {
    calculatePredictedGPA,
    formatGPA,
    getStatusColor,
    countCoursesByStatus
};

// ========================================
// Console Info
// ========================================

console.log('%c🎓 A2S Degree Audit System', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('%cDegree audit page loaded successfully', 'color: #10b981; font-size: 12px;');
