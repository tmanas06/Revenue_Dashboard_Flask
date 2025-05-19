import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

// Helper function to safely access nested properties
const safeGet = (obj, path, defaultValue = []) => {
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result === null || result === undefined) return defaultValue;
    result = result[key];
  }
  
  return result !== undefined ? result : defaultValue;
};

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    revenueSummary: { months: [], subscription_revenue: [], product_revenue: [], total_revenue: [] },
    revenueByCountry: { countries: [], revenue: [], customer_counts: [] },
    recentTransactions: [],
    planDistribution: { plans: [], subscribers: [], active_subscribers: [] }
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch all data in parallel
        const [
          revenueRes, 
          countryRes, 
          transactionsRes, 
          plansRes
        ] = await Promise.all([
          fetch('http://localhost:5000/api/dashboard/revenue-summary')
            .then(res => res.ok ? res.json() : { months: [] })
            .catch(() => ({ months: [] })),
            
          fetch('http://localhost:5000/api/dashboard/revenue-by-country')
            .then(res => res.ok ? res.json() : { countries: [] })
            .catch(() => ({ countries: [] })),
            
          fetch('http://localhost:5000/api/dashboard/recent-transactions')
            .then(res => res.ok ? res.json() : [])
            .catch(() => []),
            
          fetch('http://localhost:5000/api/dashboard/plan-distribution')
            .then(res => res.ok ? res.json() : { plans: [] })
            .catch(() => ({ plans: [] }))
        ]);

        setDashboardData({
          revenueSummary: {
            months: safeGet(revenueRes, 'months', []),
            subscription_revenue: safeGet(revenueRes, 'subscription_revenue', []),
            product_revenue: safeGet(revenueRes, 'product_revenue', []),
            total_revenue: safeGet(revenueRes, 'total_revenue', [])
          },
          revenueByCountry: {
            countries: safeGet(countryRes, 'countries', []),
            revenue: safeGet(countryRes, 'revenue', []),
            customer_counts: safeGet(countryRes, 'customer_counts', [])
          },
          recentTransactions: Array.isArray(transactionsRes) ? transactionsRes : [],
          planDistribution: {
            plans: safeGet(plansRes, 'plans', []),
            subscribers: safeGet(plansRes, 'subscribers', []),
            active_subscribers: safeGet(plansRes, 'active_subscribers', [])
          }
        });
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading dashboard data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  const { revenueSummary, revenueByCountry, recentTransactions, planDistribution } = dashboardData;
  const hasRevenueData = revenueSummary.months && revenueSummary.months.length > 0;
  const hasCountryData = revenueByCountry.countries && revenueByCountry.countries.length > 0;
  const hasPlanData = planDistribution.plans && planDistribution.plans.length > 0;
  const hasTransactions = recentTransactions && recentTransactions.length > 0;

  return (
    <div className="dashboard">
      <h1>Revenue Dashboard</h1>
      
      {/* Revenue Summary Chart */}
      <div className="chart-container">
        <h2>Monthly Revenue Overview</h2>
        {hasRevenueData ? (
          <div style={{ width: '100%', height: 400 }}>
            <ResponsiveContainer>
              <BarChart
                data={revenueSummary.months.map((month, i) => ({
                  name: month,
                  'Subscription': revenueSummary.subscription_revenue[i] || 0,
                  'Products': revenueSummary.product_revenue[i] || 0,
                  'Total': revenueSummary.total_revenue[i] || 0
                }))}
                margin={{
                  top: 20, right: 30, left: 20, bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="Subscription" fill="#8884d8" />
                <Bar dataKey="Products" fill="#82ca9d" />
                <Bar dataKey="Total" fill="#ffc658" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="no-data">No revenue data available</div>
        )}
      </div>

      <div className="dashboard-row">
        {/* Revenue by Country */}
        <div className="chart-container half-width">
          <h2>Top 10 Countries by Revenue</h2>
          {hasCountryData ? (
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <BarChart
                  data={revenueByCountry.countries.map((country, i) => ({
                    name: country,
                    revenue: (revenueByCountry.revenue && revenueByCountry.revenue[i]) || 0,
                    customers: (revenueByCountry.customer_counts && revenueByCountry.customer_counts[i]) || 0
                  }))}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={80} />
                  <Tooltip 
                    formatter={(value, name) => 
                      name === 'revenue' ? `$${value.toLocaleString()}` : value
                    }
                  />
                  <Legend />
                  <Bar dataKey="revenue" fill="#8884d8" name="Revenue" />
                  <Bar dataKey="customers" fill="#82ca9d" name="Customers" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="no-data">No country data available</div>
          )}
        </div>

        {/* Plan Distribution */}
        <div className="chart-container half-width">
          <h2>Plan Distribution</h2>
          {hasPlanData ? (
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={planDistribution.plans.map((plan, i) => ({
                      name: plan,
                      value: (planDistribution.subscribers && planDistribution.subscribers[i]) || 0,
                      active: (planDistribution.active_subscribers && planDistribution.active_subscribers[i]) || 0
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => 
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {planDistribution.plans.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name, props) => {
                      const active = (props?.payload?.active) || 0;
                      const total = value || 1; // Prevent division by zero
                      return [
                        `${name}: ${value} (${Math.round((active / total) * 100)}% active)`,
                        'Subscribers'
                      ];
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="no-data">No plan distribution data available</div>
          )}
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="chart-container">
        <h2>Recent Transactions</h2>
        {hasTransactions ? (
          <div className="transactions-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Payment Method</th>
                  <th>Product Purchase</th>
                </tr>
              </thead>
              <tbody>
                {recentTransactions.map((txn, index) => {
                  const txnDate = txn.date || txn.payment_date || 'N/A';
                  const customerName = txn.customer || txn.customer_name || 'Unknown';
                  const amount = txn.amount || 0;
                  const paymentMethod = txn.payment_method || 'N/A';
                  const hasProduct = txn.has_product_sale || txn.product_purchase || false;
                  
                  return (
                    <tr key={index}>
                      <td>{txnDate}</td>
                      <td>{customerName}</td>
                      <td>${amount.toFixed(2)}</td>
                      <td>{paymentMethod}</td>
                      <td>{hasProduct ? 'Yes' : 'No'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-data">No recent transactions available</div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
