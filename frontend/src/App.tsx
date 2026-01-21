import { useEffect, useState } from 'react';
import { fetchMetrics, seedData } from './api';
import { DashboardData } from './types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        try {
            const metrics = await fetchMetrics();
            setData(metrics);
        } catch (e) {
            console.error("Failed to load metrics", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleSeed = async () => {
        await seedData();
        loadData();
    };

    if (loading) return <div className="p-10 text-center">Loading Dashboard...</div>;
    if (!data) return <div className="p-10 text-center">Error loading data. Is the backend running?</div>;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <div className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">AI Factory Dashboard</h1>
                    <div className="space-x-4">
                        <button
                            onClick={handleSeed}
                            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition"
                        >
                            Seed Data
                        </button>
                        <button
                            onClick={loadData}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                        >
                            Refresh
                        </button>
                    </div>
                </div>

                {/* Factory Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <Card title="Productive Time" value={`${(data.factory.total_productive_time_seconds / 3600).toFixed(1)} hrs`} />
                    <Card title="Avg Utilization" value={`${data.factory.avg_utilization_percent}%`} />
                    <Card title="Total Production" value={`${data.factory.total_production_count} units`} />
                    <Card title="Avg Prod Rate" value={`${data.factory.avg_production_rate} /hr`} />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h3 className="text-xl font-semibold mb-4">Worker Utilization (%)</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={data.workers}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="utilization_percent" fill="#4f46e5" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h3 className="text-xl font-semibold mb-4">Workstation Throughput</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={data.workstations}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="workstation_id" />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="throughput_rate" fill="#10b981" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Workers Table */}
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-xl font-semibold text-gray-800">Worker Metrics</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-600">
                            <thead className="bg-gray-100 text-gray-700 uppercase">
                                <tr>
                                    <th className="px-6 py-3">ID</th>
                                    <th className="px-6 py-3">Name</th>
                                    <th className="px-6 py-3">Active Time (m)</th>
                                    <th className="px-6 py-3">Idle Time (m)</th>
                                    <th className="px-6 py-3">Utilization</th>
                                    <th className="px-6 py-3">Units Produced</th>
                                    <th className="px-6 py-3">Units/Hr</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {data.workers.map((w) => (
                                    <tr key={w.worker_id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 font-medium">{w.worker_id}</td>
                                        <td className="px-6 py-4">{w.name}</td>
                                        <td className="px-6 py-4">{(w.total_active_time_seconds / 60).toFixed(0)}</td>
                                        <td className="px-6 py-4">{(w.total_idle_time_seconds / 60).toFixed(0)}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded text-xs font-semibold ${w.utilization_percent > 80 ? 'bg-green-100 text-green-800' :
                                                w.utilization_percent > 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                                                }`}>
                                                {w.utilization_percent}%
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">{w.total_units_produced}</td>
                                        <td className="px-6 py-4">{w.units_per_hour}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Workstations Table */}
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-xl font-semibold text-gray-800">Workstation Metrics</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-600">
                            <thead className="bg-gray-100 text-gray-700 uppercase">
                                <tr>
                                    <th className="px-6 py-3">ID</th>
                                    <th className="px-6 py-3">Type</th>
                                    <th className="px-6 py-3">Occupancy (m)</th>
                                    <th className="px-6 py-3">Utilization</th>
                                    <th className="px-6 py-3">Throughput</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {data.workstations.map((s) => (
                                    <tr key={s.workstation_id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 font-medium">{s.workstation_id}</td>
                                        <td className="px-6 py-4">{s.type}</td>
                                        <td className="px-6 py-4">{(s.occupancy_time_seconds / 60).toFixed(0)}</td>
                                        <td className="px-6 py-4">{s.utilization_percent}%</td>
                                        <td className="px-6 py-4">{s.throughput_rate}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
}

function Card({ title, value }: { title: string, value: string }) {
    return (
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
            <div className="text-gray-500 text-sm">{title}</div>
            <div className="text-2xl font-bold text-gray-800 mt-2">{value}</div>
        </div>
    );
}

export default App;
