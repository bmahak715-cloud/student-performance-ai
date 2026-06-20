// AURA Academics Custom Visualization Renderer

document.addEventListener("DOMContentLoaded", () => {
    
    // --- GLOBAL CHART CONFIG OVERRIDES ---
    Chart.defaults.color = '#8e95a5';       // Text labels color
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.04)'; // Gridlines border
    Chart.defaults.font.family = "'Inter', sans-serif";
    
    const colors = {
        low: '#10b981',    // Emerald
        med: '#f59e0b',    // Amber
        high: '#ef4444',   // Crimson
        info: '#0ea5e9',   // Azure
        infoSub: 'rgba(14, 165, 233, 0.2)',
        grid: 'rgba(255, 255, 255, 0.03)'
    };

    // ==========================================
    // 1. DASHBOARD VISUALIZATIONS
    // ==========================================
    
    // Donut Chart: Risk Distribution
    const riskCtx = document.getElementById('riskDistributionChart');
    if (riskCtx && typeof riskChartData !== 'undefined') {
        new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: riskChartData.labels,
                datasets: [{
                    data: riskChartData.counts,
                    backgroundColor: [colors.low, colors.med, colors.high],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // Line Chart: Attendance vs Predicted Marks (Class Averages)
    const attMarksCtx = document.getElementById('attendanceMarksChart');
    if (attMarksCtx && typeof classTrendData !== 'undefined') {
        new Chart(attMarksCtx, {
            type: 'line',
            data: {
                labels: classTrendData.labels,
                datasets: [
                    {
                        label: 'Attendance %',
                        data: classTrendData.attendance,
                        borderColor: colors.low,
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.3,
                        pointBackgroundColor: colors.low,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Predicted marks',
                        data: classTrendData.marks,
                        borderColor: colors.med,
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.3,
                        pointBackgroundColor: colors.med,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        min: 0,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Attendance Percentage'
                        },
                        grid: { color: colors.grid }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        min: 0,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Predicted Marks'
                        },
                        grid: { drawOnChartArea: false } // Only keep gridlines for left axis
                    }
                }
            }
        });
    }


    // ==========================================
    // 2. STUDENT DETAILS PAGE VISUALIZATIONS
    // ==========================================
    
    // Combined Line Chart: Assessment Trend vs Attendance Trend
    const studentAcadCtx = document.getElementById('studentAcadAttChart');
    if (studentAcadCtx && typeof studentChartData !== 'undefined') {
        new Chart(studentAcadCtx, {
            type: 'line',
            data: {
                labels: studentChartData.dates,
                datasets: [
                    {
                        label: 'Assessment Marks (Avg)',
                        data: studentChartData.marks,
                        borderColor: colors.info,
                        backgroundColor: colors.infoSub,
                        borderWidth: 3,
                        tension: 0.25,
                        fill: true,
                        pointBackgroundColor: colors.info,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Attendance Rate (%)',
                        data: studentChartData.attendance,
                        borderColor: colors.low,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.2,
                        pointBackgroundColor: colors.low,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        type: 'linear',
                        position: 'left',
                        min: 0,
                        max: 100,
                        title: { display: true, text: 'Marks (Avg)' },
                        grid: { color: colors.grid }
                    },
                    y1: {
                        type: 'linear',
                        position: 'right',
                        min: 0,
                        max: 100,
                        title: { display: true, text: 'Attendance (%)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    // Bar/Line: LMS usage hours vs logins
    const studentLmsCtx = document.getElementById('studentLmsChart');
    if (studentLmsCtx && typeof studentChartData !== 'undefined') {
        new Chart(studentLmsCtx, {
            type: 'bar',
            data: {
                labels: studentChartData.dates,
                datasets: [
                    {
                        label: 'LMS Platform Logins (times)',
                        data: studentChartData.logins,
                        backgroundColor: colors.med,
                        borderRadius: 6,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Weekly Study Duration (hrs)',
                        data: studentChartData.hours,
                        type: 'line',
                        borderColor: colors.info,
                        backgroundColor: 'transparent',
                        borderWidth: 2.5,
                        tension: 0.2,
                        pointBackgroundColor: colors.info,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: { display: true, text: 'Weekly Logins' },
                        grid: { color: colors.grid }
                    },
                    y1: {
                        type: 'linear',
                        position: 'right',
                        title: { display: true, text: 'Study Hours' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    // Line Chart: Academic Risk Probability Timeline
    const studentRiskCtx = document.getElementById('studentRiskTimelineChart');
    if (studentRiskCtx && typeof studentChartData !== 'undefined') {
        new Chart(studentRiskCtx, {
            type: 'line',
            data: {
                labels: studentChartData.risk_dates,
                datasets: [{
                    label: 'Academic Risk Probability (%)',
                    data: studentChartData.risk_probs,
                    borderColor: colors.high,
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: colors.high,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        min: 0,
                        max: 100,
                        title: { display: true, text: 'Risk %' },
                        grid: { color: colors.grid }
                    }
                }
            }
        });
    }
});
