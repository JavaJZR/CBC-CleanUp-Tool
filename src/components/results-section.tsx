import React from 'react';
import { Download } from 'lucide-react';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { ScrollArea } from './ui/scroll-area';
import { Card } from './ui/card';

interface ResultsSectionProps {
  cleanedData: any[];
  unmatchedData: any[];
  headers: string[];
  onExportExcel: (data: any[], filename: string) => void;
  onExportCSV: (data: any[], filename: string) => void;
}

export function ResultsSection({
  cleanedData,
  unmatchedData,
  headers,
  onExportExcel,
  onExportCSV
}: ResultsSectionProps) {
  const renderTable = (data: any[], tableHeaders: string[]) => (
    <div className="border rounded-lg">
      <ScrollArea className="h-96 w-full">
        <Table>
          <TableHeader>
            <TableRow className="bg-red-600 hover:bg-red-600">
              {tableHeaders.map((header, index) => (
                <TableHead key={index} className="text-white font-medium">
                  {header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {tableHeaders.map((header, cellIndex) => (
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
  );

  return (
    <Card className="p-6 bg-gradient-to-br from-white to-green-50 border border-green-200 shadow-lg">
      <div className="mb-6">
        <h3 className="text-lg font-medium bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-2">Clean-Up Results</h3>
        <div className="bg-green-50 p-3 rounded-lg border border-green-200">
          <p className="text-sm text-green-800">
            <strong>✅ Clean-up completed!</strong> Your data has been processed and separated into two categories:
          </p>
          <div className="mt-2 text-xs text-green-700 space-y-1">
            <p>• <strong>Cleaned Report:</strong> Records successfully matched and verified</p>
            <p>• <strong>Unmatched for Review:</strong> Records that need manual verification</p>
          </div>
        </div>
      </div>
      
      <Tabs defaultValue="cleaned" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2 bg-green-50 border border-green-200">
          <TabsTrigger value="cleaned" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-600 data-[state=active]:to-emerald-600 data-[state=active]:text-white data-[state=active]:shadow-md">
            Cleaned Report ({cleanedData.length})
          </TabsTrigger>
          <TabsTrigger value="unmatched" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-red-500 data-[state=active]:text-white data-[state=active]:shadow-md">
            Unmatched for Review ({unmatchedData.length})
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="cleaned" className="space-y-4">
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportCSV(cleanedData, 'cleaned-employee-data')}
              className="border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportExcel(cleanedData, 'cleaned-employee-data')}
              className="border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Excel
            </Button>
          </div>
          
          {renderTable(cleanedData, headers)}
          
          <p className="text-sm text-gray-500">
            Showing {cleanedData.length} active employees
          </p>
        </TabsContent>
        
        <TabsContent value="unmatched" className="space-y-4">
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportCSV(unmatchedData, 'unmatched-for-review')}
              className="border-orange-300 text-orange-700 hover:bg-orange-50 hover:border-orange-400"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportExcel(unmatchedData, 'unmatched-for-review')}
              className="border-orange-300 text-orange-700 hover:bg-orange-50 hover:border-orange-400"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Excel
            </Button>
          </div>
          
          {renderTable(unmatchedData, headers)}
          
          <p className="text-sm text-gray-500">
            Showing {unmatchedData.length} records requiring manual review
          </p>
        </TabsContent>
      </Tabs>
    </Card>
  );
}