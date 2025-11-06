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
            <TableRow className="bg-gradient-to-r from-[#CD1C18] to-[#9B1313] hover:from-[#9B1313] hover:to-[#38000A]">
              {tableHeaders.map((header, index) => (
                <TableHead key={index} className="text-white font-bold text-base">
                  {header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {tableHeaders.map((header, cellIndex) => (
                  <TableCell key={cellIndex} className="text-gray-800 font-medium text-base">
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
        <h3 className="text-3xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent mb-4 tracking-tight">Clean-Up Results</h3>
        <div className="bg-[#FFA896]/20 p-5 rounded-lg border-2 border-[#FFA896]">
          <p className="text-lg text-[#9B1313] font-black">
            <strong className="font-black text-xl">✅ Clean-up completed!</strong> Your data has been processed and separated into two categories:
          </p>
          <div className="mt-4 text-base text-[#9B1313] space-y-2.5 font-bold">
            <p>• <strong>Cleaned Report:</strong> Records successfully matched and verified</p>
            <p>• <strong>Unmatched for Review:</strong> Records that need manual verification</p>
          </div>
        </div>
      </div>
      
      <Tabs defaultValue="cleaned" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2 bg-[#FFA896]/20 border-2 border-[#FFA896]">
          <TabsTrigger value="cleaned" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#CD1C18] data-[state=active]:to-[#9B1313] data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-base">
            Cleaned Report ({cleanedData.length})
          </TabsTrigger>
          <TabsTrigger value="unmatched" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#CD1C18] data-[state=active]:to-[#9B1313] data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-base">
            Unmatched for Review ({unmatchedData.length})
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="cleaned" className="space-y-4">
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportCSV(cleanedData, 'cleaned-employee-data')}
              className="border-[#FFA896] text-[#9B1313] hover:bg-[#FFA896]/20 hover:border-[#CD1C18] font-bold"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportExcel(cleanedData, 'cleaned-employee-data')}
              className="border-[#FFA896] text-[#9B1313] hover:bg-[#FFA896]/20 hover:border-[#CD1C18] font-bold"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Excel
            </Button>
          </div>
          
          {renderTable(cleanedData, headers)}
          
          <p className="text-lg text-gray-900 font-bold">
            Showing <strong className="text-[#CD1C18] font-black">{cleanedData.length}</strong> active employees
          </p>
        </TabsContent>
        
        <TabsContent value="unmatched" className="space-y-4">
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportCSV(unmatchedData, 'unmatched-for-review')}
              className="border-[#FFA896] text-[#9B1313] hover:bg-[#FFA896]/20 hover:border-[#CD1C18] font-bold"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onExportExcel(unmatchedData, 'unmatched-for-review')}
              className="border-[#FFA896] text-[#9B1313] hover:bg-[#FFA896]/20 hover:border-[#CD1C18] font-bold"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Excel
            </Button>
          </div>
          
          {renderTable(unmatchedData, headers)}
          
          <p className="text-lg text-gray-900 font-bold">
            Showing <strong className="text-[#CD1C18] font-black">{unmatchedData.length}</strong> records requiring manual review
          </p>
        </TabsContent>
      </Tabs>
    </Card>
  );
}