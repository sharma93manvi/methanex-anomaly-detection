"""
Business Impact Calculator
Calculates ROI, cost savings, and business value metrics
"""

def calculate_roi(
    downtime_cost_per_hour=50000,
    maintenance_cost_preventive=5000,
    maintenance_cost_emergency=50000,
    hours_downtime_prevented=24,
    anomalies_detected=880,
    early_warning_hours=19.3
):
    """
    Calculate ROI and cost savings from anomaly detection system
    
    Args:
        downtime_cost_per_hour: Cost of unplanned downtime per hour
        maintenance_cost_preventive: Cost of preventive maintenance
        maintenance_cost_emergency: Cost of emergency maintenance
        hours_downtime_prevented: Hours of downtime prevented through early detection
        anomalies_detected: Number of anomalies detected
        early_warning_hours: Average early warning lead time in hours
    
    Returns:
        dict: ROI and cost savings metrics
    """
    # Cost savings from preventing downtime
    downtime_cost_saved = downtime_cost_per_hour * hours_downtime_prevented
    
    # Cost savings from preventive vs emergency maintenance
    # Assuming 10% of anomalies would have led to emergency maintenance
    emergency_maintenance_events = anomalies_detected * 0.10
    maintenance_cost_saved = emergency_maintenance_events * (maintenance_cost_emergency - maintenance_cost_preventive)
    
    # Total cost savings
    total_cost_savings = downtime_cost_saved + maintenance_cost_saved
    
    # System implementation cost (estimated)
    system_implementation_cost = 100000  # One-time cost
    annual_maintenance_cost = 20000  # Annual maintenance
    
    # ROI calculation (first year)
    net_savings_year1 = total_cost_savings - system_implementation_cost - annual_maintenance_cost
    roi_percentage = (net_savings_year1 / (system_implementation_cost + annual_maintenance_cost)) * 100 if (system_implementation_cost + annual_maintenance_cost) > 0 else 0
    
    # Payback period (months)
    monthly_savings = total_cost_savings / 12
    payback_months = (system_implementation_cost + annual_maintenance_cost) / monthly_savings if monthly_savings > 0 else 0
    
    return {
        'downtime_cost_saved': downtime_cost_saved,
        'maintenance_cost_saved': maintenance_cost_saved,
        'total_cost_savings': total_cost_savings,
        'system_implementation_cost': system_implementation_cost,
        'annual_maintenance_cost': annual_maintenance_cost,
        'net_savings_year1': net_savings_year1,
        'roi_percentage': roi_percentage,
        'payback_months': payback_months,
        'hours_downtime_prevented': hours_downtime_prevented,
        'early_warning_hours': early_warning_hours,
        'anomalies_detected': anomalies_detected,
        'emergency_maintenance_events_prevented': emergency_maintenance_events
    }

def calculate_safety_impact(
    safety_incidents_prevented=2,
    cost_per_incident=500000,
    near_misses_prevented=10,
    cost_per_near_miss=50000
):
    """
    Calculate safety impact metrics
    
    Args:
        safety_incidents_prevented: Number of safety incidents prevented
        cost_per_incident: Average cost per safety incident
        near_misses_prevented: Number of near misses prevented
        cost_per_near_miss: Average cost per near miss
    
    Returns:
        dict: Safety impact metrics
    """
    total_safety_cost_saved = (
        safety_incidents_prevented * cost_per_incident +
        near_misses_prevented * cost_per_near_miss
    )
    
    return {
        'safety_incidents_prevented': safety_incidents_prevented,
        'near_misses_prevented': near_misses_prevented,
        'total_safety_cost_saved': total_safety_cost_saved
    }

def calculate_quality_impact(
    quality_defects_prevented=50,
    cost_per_defect=1000,
    customer_complaints_prevented=10,
    cost_per_complaint=5000
):
    """
    Calculate quality impact metrics
    
    Args:
        quality_defects_prevented: Number of quality defects prevented
        cost_per_defect: Average cost per defect
        customer_complaints_prevented: Number of customer complaints prevented
        cost_per_complaint: Average cost per complaint
    
    Returns:
        dict: Quality impact metrics
    """
    total_quality_cost_saved = (
        quality_defects_prevented * cost_per_defect +
        customer_complaints_prevented * cost_per_complaint
    )
    
    return {
        'quality_defects_prevented': quality_defects_prevented,
        'customer_complaints_prevented': customer_complaints_prevented,
        'total_quality_cost_saved': total_quality_cost_saved
    }

