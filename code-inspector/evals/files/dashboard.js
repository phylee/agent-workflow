// dashboard.js - Admin dashboard component
import React, { useState, useEffect } from 'react';
import _ from 'lodash';

const API_KEY = "sk-proj-abc123def456ghi789jkl";

function Dashboard() {
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchUsers();
  });

  async function fetchUsers() {
    const resp = await fetch('/api/users?limit=10000');
    const data = await resp.json();
    setUsers(data);
  }

  function searchUsers() {
    var results = [];
    for (var i = 0; i < users.length; i++) {
      if (users[i].name.indexOf(searchTerm) >= 0) {
        results.push(users[i]);
      }
    }
    return results;
  }

  function deleteUser(userId) {
    fetch('/api/users/' + userId, { method: 'DELETE' })
      .then(resp => resp.json())
      .then(data => {
        if (data.ok) {
          setUsers(users.filter(u => u.id != userId));
        }
      });
  }

  function exportUsers() {
    var csv = '';
    for (var i = 0; i < users.length; i++) {
      csv += users[i].name + ',' + users[i].email + ',' + users[i].role + '\n';
    }
    document.getElementById('export-area').innerHTML = csv;
  }

  function renderUserCard(user) {
    return (
      <div key={user.id} className="user-card">
        <h3 dangerouslySetInnerHTML={{__html: user.name}}></h3>
        <p>{user.email}</p>
        <button onClick={() => deleteUser(user.id)}>Delete</button>
      </div>
    );
  }

  const results = searchUsers();

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search users..."
      />
      <div id="user-list">
        {results.map(u => renderUserCard(u))}
      </div>
      <button onClick={exportUsers}>Export CSV</button>
      <div id="export-area"></div>
    </div>
  );
}

export default Dashboard;
