import React, { useEffect, useState, useRef } from 'react';
import { Activity, TrendingUp, TrendingDown, DollarSign, Shield, Zap, Power } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws";

const GodfatherDashboard = () => {
    const [metrics, setMetrics] = useState(null);
    const [status, setStatus] = useState("DISCONNECTED");
    const [logs, setLogs] = useState([]);
    const ws = useRef(null);

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (ws.current) ws.current.close();
        };
    }, []);

    const connectWebSocket = () => {
        ws.current = new WebSocket(WS_URL);

        ws.current.onopen = () => {
            setStatus("LIVE");
            addLog("System Connected to Neural Core.");
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMetrics(data);
        };

        ws.current.onclose = () => {
            setStatus("OFFLINE");
            setTimeout(connectWebSocket, 3000);
        };
    };

    const addLog = (msg) => {
        setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev.slice(0, 10)]);
    };

    if (!metrics) return (
        <div className="min-h-screen bg-black text-green-500 flex items-center justify-center font-mono animate-pulse">
            INITIALIZING GODFATHER PROTOCOL...
        </div>
    );

    return (
        <div className="min-h-screen bg-black text-gray-100 font-sans selection:bg-green-900">
            {/* Header */}
            <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <Zap className="text-yellow-400 fill-yellow-400 animate-pulse" />
                        <h1 className="text-2xl font-bold tracking-tighter bg-gradient-to-r from-white to-gray-500 bg-clip-text text-transparent">
                            NK<span className="text-yellow-500">BOT</span> <span className="text-xs text-gray-500 border border-gray-700 px-2 py-0.5 rounded ml-2">GODFATHER MODE</span>
                        </h1>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold ${status === 'LIVE' ? 'bg-green-900/30 text-green-400 border border-green-800' : 'bg-red-900/30 text-red-500'}`}>
                            <div className={`w-2 h-2 rounded-full ${status === 'LIVE' ? 'bg-green-500 animate-ping' : 'bg-red-500'}`} />
                            {status}
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-6">

                {/* KPI Cards */}
                <div className="col-span-12 grid grid-cols-4 gap-4">
                    <Card title="SENTIMENT" value={metrics.sentiment?.toFixed(2)} icon={<Activity />} color="text-blue-400" />
                    <Card title="ACTIVE POSITIONS" value={Object.keys(metrics.positions || {}).length} icon={<TrendingUp />} color="text-green-400" />
                    <Card title="PNL (SESSION)" value={`₹${metrics.pnl || 0}`} icon={<DollarSign />} color="text-yellow-400" />
                    <Card title="RISK LEVEL" value="LOW" icon={<Shield />} color="text-purple-400" />
                </div>

                {/* Main Chart Area */}
                <div className="col-span-8 bg-gray-900/30 border border-gray-800 rounded-xl p-6 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <h3 className="text-sm font-semibold text-gray-400 mb-4 flex items-center gap-2">
                        <TrendingUp size={16} /> MARKET VELOCITY (Simulated)
                    </h3>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={[{ v: 10 }, { v: 15 }, { v: 8 }, { v: 22 }, { v: 18 }, { v: 35 }]}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis hide />
                                <YAxis hide />
                                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #333' }} />
                                <Line type="monotone" dataKey="v" stroke="#8884d8" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Live Logs / Positions */}
                <div className="col-span-4 bg-gray-900/30 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-sm font-semibold text-gray-400 mb-4">LIVE FEED</h3>
                    <div className="space-y-2 h-64 overflow-y-auto font-mono text-xs">
                        {logs.map((log, i) => (
                            <div key={i} className="text-gray-500 border-l-2 border-gray-800 pl-2">
                                {log}
                            </div>
                        ))}
                        {Object.keys(metrics.positions || {}).length === 0 && (
                            <div className="text-gray-600 italic">No active positions. Scanning...</div>
                        )}
                    </div>
                </div>

            </main>
        </div>
    );
};

const Card = ({ title, value, icon, color }) => (
    <div className="bg-gray-900/40 border border-gray-800 p-4 rounded-xl backdrop-blur-sm hover:border-gray-700 transition-colors">
        <div className={`mb-2 ${color}`}>{icon}</div>
        <div className="text-2xl font-bold font-mono">{value}</div>
        <div className="text-xs text-gray-500 font-semibold tracking-wider">{title}</div>
    </div>
);

export default GodfatherDashboard;
