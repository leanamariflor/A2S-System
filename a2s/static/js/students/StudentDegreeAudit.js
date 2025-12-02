
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 DOMContentLoaded event fired!');
    
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
        console.log('✓ Lucide icons initialized');
    } else {
        console.warn('⚠ Lucide library not found');
    }

   
    initializeTabs();

   
    initializeCalculator();

    
    animateProgressCircle();
    
    
    console.log('🔵 About to initialize Add to Plan...');
    initializeAddToPlan();
    console.log('✓ Add to Plan initialized');
    
    
    console.log('🔵 About to initialize Modal Listeners...');
    initializeModalListeners();
    console.log('✓ Modal Listeners initialized');
    
    
    console.log('🔵 About to update plan count...');
    updatePlanCount();
    console.log('✓ Plan count updated');
    
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

            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            
            button.classList.add('active');
            const targetContent = document.querySelector(`.category-content[data-category="${targetCategory}"]`);
            if (targetContent) {
                targetContent.classList.add('active');
            }

          
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

    
    const strokeDasharray = progressBar.getAttribute('style');
    const match = strokeDasharray.match(/stroke-dasharray:\s*([\d.]+)/);
    
    if (match) {
        const percentage = parseFloat(match[1]);
        const circumference = 2 * Math.PI * 75; 
        const offset = circumference - (percentage / 100) * circumference;

        
        progressBar.style.strokeDasharray = circumference;
        progressBar.style.strokeDashoffset = circumference;

        setTimeout(() => {
            progressBar.style.transition = 'stroke-dashoffset 1.5s ease-in-out';
            progressBar.style.strokeDashoffset = offset;
        }, 100);
    }
}

// ========================================
// Add to Plan Functionality
// ========================================

function initializeAddToPlan() {
    const addToPlanButtons = document.querySelectorAll('.btn-add-to-plan');
    
    console.log('Initializing Add to Plan. Found buttons:', addToPlanButtons.length);
    
   
    const savedPlans = JSON.parse(localStorage.getItem('studentCoursePlan') || '[]');
    
    
    savedPlans.forEach(courseCode => {
        const button = document.querySelector(`.btn-add-to-plan[data-course-code="${courseCode}"]`);
        if (button) {
            markAsAdded(button);
        }
    });
   
    addToPlanButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            console.log('Button clicked!', this);
            
            const courseCode = this.getAttribute('data-course-code');
            const courseTitle = this.getAttribute('data-course-title');
            const courseUnits = this.getAttribute('data-course-units');
            
            console.log('Course data:', { courseCode, courseTitle, courseUnits });
            
          
            if (this.classList.contains('added')) {
                
                removeFromPlan(courseCode, this);
                showNotification(`${courseCode} removed from your plan`, 'info');
            } else {
               
                addToPlan(courseCode, courseTitle, courseUnits, this);
                showNotification(`${courseCode} added to your plan!`, 'success');
            }
        });
    });
}

// ========================================
// Modal Event Listeners
// ========================================

function initializeModalListeners() {
    console.log('Initializing modal event listeners...');
    
   
    const viewPlanBtn = document.getElementById('viewPlanBtn');
    if (viewPlanBtn) {
        viewPlanBtn.addEventListener('click', function() {
            console.log('View Plan button clicked');
            toggleCoursePlan();
        });
        console.log('✓ View Plan button listener added');
    } else {
        console.warn('⚠ View Plan button not found');
    }
    
    
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', function() {
            console.log('Close button clicked');
            toggleCoursePlan();
        });
        console.log('✓ Modal close button listener added');
    }
    
    
    const modalCloseBtn2 = document.getElementById('modalCloseBtn2');
    if (modalCloseBtn2) {
        modalCloseBtn2.addEventListener('click', function() {
            console.log('Close button 2 clicked');
            toggleCoursePlan();
        });
        console.log('✓ Modal close button 2 listener added');
    }
    
    
    const modalOverlay = document.getElementById('modalOverlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function() {
            console.log('Overlay clicked');
            toggleCoursePlan();
        });
        console.log('✓ Modal overlay listener added');
    }
    
   
    const clearPlanBtn = document.getElementById('clearPlanBtn');
    if (clearPlanBtn) {
        clearPlanBtn.addEventListener('click', function() {
            console.log('Clear Plan button clicked');
            clearAllPlan();
        });
        console.log('✓ Clear Plan button listener added');
    }
}

function addToPlan(courseCode, courseTitle, courseUnits, button) {
    
    let plans = JSON.parse(localStorage.getItem('studentCoursePlan') || '[]');
    let planDetails = JSON.parse(localStorage.getItem('studentCoursePlanDetails') || '[]');
    
   
    if (!plans.includes(courseCode)) {
        plans.push(courseCode);
    }
    
   
    const courseExists = planDetails.some(course => course.code === courseCode);
    if (!courseExists) {
        planDetails.push({
            code: courseCode,
            title: courseTitle,
            units: parseInt(courseUnits),
            addedDate: new Date().toISOString()
        });
    }
    
   
    localStorage.setItem('studentCoursePlan', JSON.stringify(plans));
    localStorage.setItem('studentCoursePlanDetails', JSON.stringify(planDetails));
    
    
    markAsAdded(button);
    
    const card = button.closest('.recommendation-card');
    if (card) {
        card.classList.add('added-to-plan');
    }
    
    updatePlanCount();
}

function removeFromPlan(courseCode, button) {

    let plans = JSON.parse(localStorage.getItem('studentCoursePlan') || '[]');
    let planDetails = JSON.parse(localStorage.getItem('studentCoursePlanDetails') || '[]');
    
    plans = plans.filter(code => code !== courseCode);
    planDetails = planDetails.filter(course => course.code !== courseCode);
    
    localStorage.setItem('studentCoursePlan', JSON.stringify(plans));
    localStorage.setItem('studentCoursePlanDetails', JSON.stringify(planDetails));
    
    markAsRemoved(button);
    
    const card = button.closest('.recommendation-card');
    if (card) {
        card.classList.remove('added-to-plan');
    }
    
    updatePlanCount();
}

function markAsAdded(button) {
    button.classList.add('added');
    button.style.background = '#22c55e';
    button.style.borderColor = '#22c55e';
    
    const icon = button.querySelector('i');
    const textSpan = button.querySelector('.btn-text');
    
    if (icon) {
        icon.setAttribute('data-lucide', 'check');
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    if (textSpan) {
        textSpan.textContent = 'Added to Plan';
    }
    
    const card = button.closest('.recommendation-card');
    if (card) {
        card.classList.add('added-to-plan');
    }
}

function markAsRemoved(button) {
    button.classList.remove('added');
    button.style.background = '';
    button.style.borderColor = '';
    
    const icon = button.querySelector('i');
    const textSpan = button.querySelector('.btn-text');
    
    if (icon) {
        icon.setAttribute('data-lucide', 'plus');
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    if (textSpan) {
        textSpan.textContent = 'Add to Plan';
    }
}

function showNotification(message, type = 'success') {

    const existingNotification = document.querySelector('.course-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `course-notification ${type}`;
    notification.innerHTML = `
        <i data-lucide="${type === 'success' ? 'check-circle' : 'info'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function getPlannedCourses() {
    return JSON.parse(localStorage.getItem('studentCoursePlanDetails') || '[]');
}

// ========================================
// Course Plan Modal Functions
// ========================================

function toggleCoursePlan() {
    const modal = document.getElementById('coursePlanModal');
    if (!modal) {
        console.error('❌ Course plan modal not found!');
        return;
    }
    
    console.log('Toggle modal called. Current display:', modal.style.display);
    
    if (modal.style.display === 'none' || modal.style.display === '') {

        modal.style.display = 'flex';
        renderCoursePlan();
        document.body.style.overflow = 'hidden';
        console.log('✓ Modal opened');
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } else {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        console.log('✓ Modal closed');
    }
}

function renderCoursePlan() {
    const planList = document.getElementById('coursePlanList');
    const plans = getPlannedCourses();
    
    console.log('Rendering course plan. Courses:', plans.length);
    
    if (!planList) {
        console.error('❌ Course plan list element not found!');
        return;
    }
    
    if (plans.length === 0) {
        planList.innerHTML = '<p class="empty-plan">No courses added to your plan yet. Start by clicking "Add to Plan" on recommended courses!</p>';
        document.getElementById('totalPlanUnits').textContent = '0';
        document.getElementById('totalPlanCourses').textContent = '0';
        return;
    }
    
    let totalUnits = 0;
    let html = '';
    
    plans.forEach((course, index) => {
        totalUnits += course.units;
        const addedDate = new Date(course.addedDate).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
        
        html += `
            <div class="plan-item" data-course-code="${course.code}">
                <div class="plan-item-header">
                    <span class="plan-number">${index + 1}</span>
                    <div class="plan-item-info">
                        <h4>${course.code}</h4>
                        <p>${course.title}</p>
                        <span class="plan-date">Added: ${addedDate}</span>
                    </div>
                    <span class="plan-units">${course.units} units</span>
                </div>
                <button class="btn-remove-from-plan" onclick="removeFromPlanModal('${course.code}')">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `;
    });
    
    planList.innerHTML = html;
    document.getElementById('totalPlanUnits').textContent = totalUnits;
    document.getElementById('totalPlanCourses').textContent = plans.length;
    
    console.log('✓ Course plan rendered');
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

window.removeFromPlanModal = function(courseCode) {
    const button = document.querySelector(`.btn-add-to-plan[data-course-code="${courseCode}"]`);
    
    if (button) {
        removeFromPlan(courseCode, button);
    } else {
        let plans = JSON.parse(localStorage.getItem('studentCoursePlan') || '[]');
        let planDetails = JSON.parse(localStorage.getItem('studentCoursePlanDetails') || '[]');
        
        plans = plans.filter(code => code !== courseCode);
        planDetails = planDetails.filter(course => course.code !== courseCode);
        
        localStorage.setItem('studentCoursePlan', JSON.stringify(plans));
        localStorage.setItem('studentCoursePlanDetails', JSON.stringify(planDetails));
    }
    
    renderCoursePlan();
    updatePlanCount();
    showNotification(`${courseCode} removed from your plan`, 'info');
}

function clearAllPlan() {
    console.log('Clear all plan called');
    if (confirm('Are you sure you want to clear all courses from your plan?')) {
        
        localStorage.setItem('studentCoursePlan', '[]');
        localStorage.setItem('studentCoursePlanDetails', '[]');
        
        
        const buttons = document.querySelectorAll('.btn-add-to-plan.added');
        buttons.forEach(button => {
            markAsRemoved(button);
        });
        
        
        renderCoursePlan();
        updatePlanCount();
        showNotification('All courses cleared from your plan', 'info');
    }
}

function updatePlanCount() {
    const planCountElement = document.getElementById('planCount');
    if (planCountElement) {
        const plans = getPlannedCourses();
        planCountElement.textContent = plans.length;
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

       
        const selectedOption = courseSelect.options[courseSelect.selectedIndex];
        const courseUnits = parseInt(selectedOption.getAttribute('data-units')) || 3;

     
        const result = calculatePredictedGPA(
            currentGPA,
            completedUnits,
            parseFloat(selectedGrade),
            courseUnits
        );

        
        displayCalculatorResult(result, resultDiv, predictedGpaSpan, gpaChangeSpan);
    });
}

/**
 * @param {number} currentGPA 
 * @param {number} currentUnits 
 * @param {number} expectedGrade
 * @param {number} courseUnits
 * @returns {object} 
 */
function calculatePredictedGPA(currentGPA, currentUnits, expectedGrade, courseUnits) {

    const currentGradePoints = currentGPA * currentUnits;

    const newGradePoints = expectedGrade * courseUnits;

    const newTotalUnits = currentUnits + courseUnits;

    const predictedGPA = (currentGradePoints + newGradePoints) / newTotalUnits;

    const gpaChange = predictedGPA - currentGPA;

    return {
        predictedGPA: predictedGPA,
        change: gpaChange,
        isImprovement: gpaChange > 0,
        isDecline: gpaChange < 0
    };
}


function displayCalculatorResult(result, resultDiv, predictedGpaSpan, gpaChangeSpan) {

    predictedGpaSpan.textContent = result.predictedGPA.toFixed(2);

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

    resultDiv.style.display = 'block';

    setTimeout(() => {
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// ========================================
// Course Card Interactions
// ========================================

document.addEventListener('click', (e) => {
    const courseCard = e.target.closest('.course-card');
    if (courseCard) {
        
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


function formatGPA(gpa) {
    return parseFloat(gpa).toFixed(2);
}


function getStatusColor(status) {
    const colors = {
        'PASSED': '#10b981',
        'CURRENT': '#f59e0b',
        'RECOMMENDED': '#06b6d4'
    };
    return colors[status.toUpperCase()] || '#64748b';
}


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
    countCoursesByStatus,
    getPlannedCourses,
    addToPlan,
    removeFromPlan
};

// ========================================
// Console Info
// ========================================

console.log('%c🎓 A2S Degree Audit System', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('%cDegree audit page loaded successfully', 'color: #10b981; font-size: 12px;');

// ========================================
// Diagnostic Check (Run after page loads)
// ========================================

setTimeout(() => {
    console.log('=== ADD TO PLAN DIAGNOSTIC ===');
    console.log('Add to Plan buttons found:', document.querySelectorAll('.btn-add-to-plan').length);
    console.log('View Plan button found:', document.getElementById('viewPlanBtn') ? 'YES' : 'NO');
    console.log('Modal found:', document.getElementById('coursePlanModal') ? 'YES' : 'NO');
    console.log('Current plan:', JSON.parse(localStorage.getItem('studentCoursePlan') || '[]'));
    console.log('===========================');
}, 1000);