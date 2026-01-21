export interface WorkerMetric {
    worker_id: string;
    name: string;
    total_active_time_seconds: number;
    total_idle_time_seconds: number;
    utilization_percent: number;
    total_units_produced: number;
    units_per_hour: number;
}

export interface WorkstationMetric {
    workstation_id: string;
    type: string;
    occupancy_time_seconds: number;
    utilization_percent: number;
    total_units_produced: number;
    throughput_rate: number;
}

export interface FactoryMetrics {
    total_productive_time_seconds: number;
    total_production_count: number;
    avg_production_rate: number;
    avg_utilization_percent: number;
}

export interface DashboardData {
    factory: FactoryMetrics;
    workers: WorkerMetric[];
    workstations: WorkstationMetric[];
}
