"""
Recommendations Engine - Generates actionable recommendations based on predictions
"""

from datetime import datetime, timedelta


def generate_recommendations(prediction_results, severity_level, root_cause, lead_time_hours=None):
    """
    Generate actionable recommendations based on predictions
    
    Args:
        prediction_results: Dictionary with prediction results
        severity_level: Severity level ('Low', 'Medium', 'High', 'Critical')
        root_cause: Root cause analysis results
        lead_time_hours: Predicted lead time in hours
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Check if we have a future prediction (even if no current anomalies)
    has_future_prediction = (
        prediction_results.get('predicted_timestamp') is not None and
        prediction_results.get('confidence', 0) > 0.3
    )
    
    # If we have future prediction but low severity, still generate recommendations
    if has_future_prediction and severity_level == 'Low':
        lead_display = lead_time_hours if lead_time_hours is not None else 24
        recommendations.append({
            'priority': 'Medium',
            'title': 'Proactive Monitoring Recommended',
            'description': f'Early warning indicators detected. Anomaly predicted in {lead_display:.1f} hours if current trends continue.',
            'actions': [
                'Increase monitoring frequency for key sensors',
                'Review sensor calibration and maintenance schedules',
                'Prepare maintenance resources',
                'Document current operating conditions'
            ],
            'timeline': f'Within {int(lead_display)} hours'
        })
    
    # Severity-based recommendations
    if severity_level == 'Critical':
        recommendations.append({
            'priority': 'Critical',
            'title': 'Immediate Action Required',
            'description': 'Critical anomaly detected. Initiate emergency response procedures immediately.',
            'actions': [
                'Alert operations team immediately',
                'Review all safety systems',
                'Prepare for potential shutdown',
                'Notify management and safety team'
            ],
            'timeline': 'Immediate'
        })
    
    elif severity_level == 'High':
        recommendations.append({
            'priority': 'High',
            'title': 'Urgent Investigation Required',
            'description': 'High severity anomaly detected. Investigate root cause immediately.',
            'actions': [
                'Increase monitoring frequency',
                'Review recent operational changes',
                'Check related equipment',
                'Prepare maintenance team'
            ],
            'timeline': 'Within 2 hours'
        })
    
    elif severity_level == 'Medium':
        recommendations.append({
            'priority': 'Medium',
            'title': 'Schedule Investigation',
            'description': 'Medium severity anomaly detected. Schedule investigation and monitoring.',
            'actions': [
                'Monitor sensor trends closely',
                'Review historical patterns',
                'Schedule maintenance window',
                'Document observations'
            ],
            'timeline': 'Within 24 hours'
        })
    
    else:  # Low
        recommendations.append({
            'priority': 'Low',
            'title': 'Monitor and Document',
            'description': 'Low severity anomaly detected. Continue monitoring.',
            'actions': [
                'Continue normal monitoring',
                'Document in maintenance log',
                'Review during next scheduled inspection'
            ],
            'timeline': 'Routine monitoring'
        })
    
    # Lead time-based recommendations
    if lead_time_hours is not None:
        if lead_time_hours > 24:
            recommendations.append({
                'priority': 'Medium',
                'title': 'Proactive Maintenance Window Available',
                'description': f'Anomaly predicted in {lead_time_hours:.1f} hours. Sufficient time for proactive action.',
                'actions': [
                    'Schedule preventive maintenance',
                    'Order replacement parts if needed',
                    'Plan maintenance window',
                    'Coordinate with operations team'
                ],
                'timeline': f'Within {int(lead_time_hours)} hours'
            })
        elif lead_time_hours > 12:
            recommendations.append({
                'priority': 'High',
                'title': 'Prepare for Maintenance',
                'description': f'Anomaly predicted in {lead_time_hours:.1f} hours. Prepare maintenance resources.',
                'actions': [
                    'Prepare maintenance team',
                    'Review maintenance procedures',
                    'Ensure parts availability',
                    'Coordinate shutdown if needed'
                ],
                'timeline': f'Within {int(lead_time_hours)} hours'
            })
        else:
            recommendations.append({
                'priority': 'High',
                'title': 'Immediate Preparation Required',
                'description': f'Anomaly predicted in {lead_time_hours:.1f} hours. Limited time for action.',
                'actions': [
                    'Alert maintenance team immediately',
                    'Prepare emergency procedures',
                    'Review contingency plans',
                    'Ensure team availability'
                ],
                'timeline': 'Immediate'
            })
    
    # Root cause-based recommendations
    if root_cause and root_cause.get('primary_cause'):
        primary_sensor = root_cause['primary_cause'].get('sensor', 'Unknown')
        
        if 'Pressure' in primary_sensor:
            recommendations.append({
                'priority': 'Medium',
                'title': 'Pressure System Investigation',
                'description': f'Root cause identified in pressure system: {primary_sensor}',
                'actions': [
                    'Check pressure relief valves',
                    'Inspect pressure sensors for calibration',
                    'Review pressure control systems',
                    'Check for leaks or blockages'
                ],
                'timeline': 'Within 8 hours'
            })
        
        elif 'Speed' in primary_sensor:
            recommendations.append({
                'priority': 'Medium',
                'title': 'Speed Control System Investigation',
                'description': f'Root cause identified in speed system: {primary_sensor}',
                'actions': [
                    'Check speed sensors for calibration',
                    'Review speed control systems',
                    'Inspect mechanical components',
                    'Review vibration data'
                ],
                'timeline': 'Within 8 hours'
            })
        
        elif 'Flow' in primary_sensor:
            recommendations.append({
                'priority': 'Medium',
                'title': 'Flow System Investigation',
                'description': f'Root cause identified in flow system: {primary_sensor}',
                'actions': [
                    'Check flow sensors for calibration',
                    'Inspect flow control valves',
                    'Review flow control systems',
                    'Check for blockages'
                ],
                'timeline': 'Within 8 hours'
            })
    
    # Contributing factors recommendations
    if root_cause and root_cause.get('contributing_factors'):
        num_factors = len(root_cause['contributing_factors'])
        if num_factors >= 3:
            recommendations.append({
                'priority': 'High',
                'title': 'Multiple Contributing Factors',
                'description': f'{num_factors} sensors showing deviations. May indicate systemic issue.',
                'actions': [
                    'Review overall system health',
                    'Check for common root causes',
                    'Consider comprehensive maintenance',
                    'Review operational procedures'
                ],
                'timeline': 'Within 12 hours'
            })
    
    # Sort by priority
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    return recommendations


def format_recommendations_for_display(recommendations):
    """
    Format recommendations for Streamlit display
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        Formatted string for display
    """
    if not recommendations:
        return "No specific recommendations at this time."
    
    formatted = []
    for i, rec in enumerate(recommendations, 1):
        formatted.append(f"**{i}. {rec['title']}** ({rec['priority']} Priority)")
        formatted.append(f"   {rec['description']}")
        formatted.append(f"   **Timeline:** {rec['timeline']}")
        formatted.append(f"   **Actions:**")
        for action in rec['actions']:
            formatted.append(f"   - {action}")
        formatted.append("")
    
    return "\n".join(formatted)

