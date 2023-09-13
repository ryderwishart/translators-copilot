'use client'

import React from 'react';

interface Table {
  name: string;
  columns: string[];
  num_rows: number;
  rows: string[];
}

interface DatabaseInfoProps {
  dbInfo: Table[];
}

export const DatabaseInfo: React.FC<DatabaseInfoProps> = ({ dbInfo }) => {
  if (!dbInfo) {
    return <div>dbInfo is undefined</div>;
  }

  return (
    <div>
      {dbInfo && (
        <table>
          <thead>
            <tr>
              <th>Table Name (or Language Code)</th>
              <th>Columns in Table</th>
              <th>Num Rows in Table</th>
              <th>Sample Row</th>
            </tr>
          </thead>
          <tbody>
            {dbInfo.map((table: Table) => (
              <tr key={table.name}>
                <td>{table.name}</td>
                <td>{JSON.stringify(table.columns)}</td>
                <td>{table.num_rows}</td>
                <td>{table.rows[0]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

