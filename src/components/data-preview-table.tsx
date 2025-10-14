import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { ScrollArea } from './ui/scroll-area';

interface DataPreviewTableProps {
  title: string;
  data: any[];
  headers: string[];
}

export function DataPreviewTable({ title, data, headers }: DataPreviewTableProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredData = data.filter(row =>
    Object.values(row).some(value =>
      String(value).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const displayData = filteredData.slice(0, 20);

  return (
    <div className="space-y-4 bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-blue-100 shadow-lg">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{title}</h3>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-400 w-4 h-4" />
          <Input
            placeholder="Search data..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 rounded-lg border-blue-200 focus:border-blue-400 bg-white/80"
          />
        </div>
      </div>
      
      <div className="border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <ScrollArea className="h-96 w-full">
          <Table>
            <TableHeader>
              <TableRow className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-600 hover:to-red-700">
                {headers.map((header, index) => (
                  <TableHead key={index} className="text-white font-medium">
                    {header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayData.map((row, rowIndex) => (
                <TableRow key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white hover:bg-blue-50' : 'bg-blue-25 hover:bg-blue-75'}>
                  {headers.map((header, cellIndex) => (
                    <TableCell key={cellIndex} className="text-gray-700">
                      {String(row[header] || '')}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </ScrollArea>
      </div>
      <p className="text-sm text-gray-500">
        Showing {displayData.length} of {filteredData.length} rows
      </p>
    </div>
  );
}