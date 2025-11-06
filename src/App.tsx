import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import { FileUploadCard } from './components/file-upload-card';
import { DataPreviewTable } from './components/data-preview-table';
import { CleanupControls } from './components/cleanup-controls';
import { ResultsSection } from './components/results-section';
import { Separator } from './components/ui/separator';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';

interface UploadedFile {
  file: File;
  data: any[];
  headers: string[];
}

interface UploadedFiles {
  currentSystem?: UploadedFile;
  previousReference?: UploadedFile;
  masterlistCurrent?: UploadedFile;
  masterlistResigned?: UploadedFile;
}

export default function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFiles>({});
  const [currentStep, setCurrentStep] = useState(1);
  const [threshold, setThreshold] = useState(80);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('Ready to start clean-up');
  const [cleanedData, setCleanedData] = useState<any[]>([]);
  const [unmatchedData, setUnmatchedData] = useState<any[]>([]);
  const [selectedPreviewFile, setSelectedPreviewFile] = useState<keyof UploadedFiles | null>(null);
  const [uploadingFiles, setUploadingFiles] = useState<Set<keyof UploadedFiles>>(new Set());
  
  const summaryCounts = {
    total: Object.values(uploadedFiles).reduce((sum, file) => sum + (file?.data.length || 0), 0),
    matched: cleanedData.length,
    unmatched: unmatchedData.length
  };

  // Mock data for demonstration
  const generateMockData = (type: string) => {
    const baseData = [
      { employeeId: '12345', name: 'Juan Dela Cruz', department: 'IT', position: 'Developer', email: 'juan.delacruz@chinabank.ph' },
      { employeeId: '12346', name: 'Maria Santos', department: 'HR', position: 'Manager', email: 'maria.santos@chinabank.ph' },
      { employeeId: '12347', name: 'Jose Rodriguez', department: 'Finance', position: 'Analyst', email: 'jose.rodriguez@chinabank.ph' },
      { employeeId: '12348', name: 'Ana Garcia', department: 'Operations', position: 'Supervisor', email: 'ana.garcia@chinabank.ph' },
      { employeeId: '12349', name: 'Carlos Mendoza', department: 'IT', position: 'Senior Developer', email: 'carlos.mendoza@chinabank.ph' },
    ];
    
    return Array.from({ length: 50 }, (_, i) => ({
      ...baseData[i % baseData.length],
      employeeId: String(12345 + i),
      name: `${baseData[i % baseData.length].name} ${i + 1}`,
      status: type === 'resigned' ? 'Resigned' : 'Active'
    }));
  };

  const parseCsvText = (text: string): { data: any[], headers: string[] } => {
    const lines = text.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
      throw new Error('File is empty');
    }
    
    // Better CSV parsing that handles quoted fields
    const parseCSVLine = (line: string): string[] => {
      const result = [];
      let current = '';
      let inQuotes = false;
      
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          result.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      
      result.push(current.trim());
      return result;
    };
    
    const headers = parseCSVLine(lines[0]).map(h => h.replace(/^["']|["']$/g, ''));
    const data = lines.slice(1).map(line => {
      const values = parseCSVLine(line).map(v => v.replace(/^["']|["']$/g, ''));
      const row: any = {};
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
      return row;
    });
    
    return { data, headers };
  };

  const parseFile = async (file: File): Promise<{ data: any[], headers: string[] }> => {
    return new Promise((resolve, reject) => {
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      
      if (fileExtension === 'csv') {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const text = e.target?.result as string;
            const result = parseCsvText(text);
            resolve(result);
          } catch (error) {
            reject(new Error(`Failed to parse CSV file: ${error instanceof Error ? error.message : 'Unknown error'}`));
          }
        };
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsText(file);
        
      } else if (fileExtension === 'xlsx' || fileExtension === 'xls') {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const arrayBuffer = e.target?.result as ArrayBuffer;
            const workbook = XLSX.read(arrayBuffer, { type: 'array' });
            
            // Get the first worksheet
            const sheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[sheetName];
            
            // Convert to JSON
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];
            
            if (jsonData.length === 0) {
              reject(new Error('Excel file is empty'));
              return;
            }
            
            // Extract headers and data
            const headers = jsonData[0].map(h => String(h || '').trim());
            const data = jsonData.slice(1).map(row => {
              const rowData: any = {};
              headers.forEach((header, index) => {
                rowData[header] = String(row[index] || '').trim();
              });
              return rowData;
            });
            
            resolve({ data, headers });
          } catch (error) {
            reject(new Error(`Failed to parse Excel file: ${error instanceof Error ? error.message : 'Unknown error'}`));
          }
        };
        reader.onerror = () => reject(new Error('Failed to read Excel file'));
        reader.readAsArrayBuffer(file);
        
      } else {
        reject(new Error('Unsupported file format. Please upload CSV, XLS, or XLSX files.'));
      }
    });
  };

  const handleFileUpload = async (fileType: keyof UploadedFiles, file: File) => {
    try {
      setUploadingFiles(prev => new Set(prev).add(fileType));
      setStatusText(`Parsing ${file.name}...`);
      
      // Validate file size (50MB limit)
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        throw new Error('File size exceeds 50MB limit');
      }
      
      const { data, headers } = await parseFile(file);
      
      // Validate parsed data
      if (!data || data.length === 0) {
        throw new Error('No data found in file');
      }
      
      if (!headers || headers.length === 0) {
        throw new Error('No column headers found in file');
      }
      
      setUploadedFiles(prev => ({
        ...prev,
        [fileType]: {
          file,
          data,
          headers
        }
      }));

      // Set this file as the selected preview file
      setSelectedPreviewFile(fileType);

      // Auto-advance to step 2 when first file is uploaded
      if (currentStep === 1) {
        setCurrentStep(2);
      }
      
      setStatusText(`Successfully loaded ${data.length} records from ${file.name}`);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setStatusText('Ready to start clean-up');
      }, 3000);
      
    } catch (error) {
      console.error('File parsing error:', error);
      
      // Show user-friendly error message
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Error parsing "${file.name}": ${errorMessage}\n\nPlease ensure your file:\n• Is a valid CSV, XLS, or XLSX file\n• Contains column headers in the first row\n• Is not corrupted or password-protected\n• Is smaller than 50MB`);
      
      setStatusText('Ready to start clean-up');
    } finally {
      setUploadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileType);
        return newSet;
      });
    }
  };

  const runCleanup = () => {
    setIsRunning(true);
    setProgress(0);
    setStatusText('Starting data clean-up process...');

    // Simulate cleanup process
    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + 10;
        
        if (newProgress <= 30) {
          setStatusText('Loading and validating data...');
        } else if (newProgress <= 60) {
          setStatusText('Matching records using fuzzy logic...');
        } else if (newProgress <= 90) {
          setStatusText('Generating clean reports...');
        } else if (newProgress >= 100) {
          setStatusText('Clean-up completed successfully!');
          setIsRunning(false);
          setCurrentStep(4);
          
          // Generate mock results
          const allData = uploadedFiles.currentSystem?.data || [];
          const cleaned = allData.slice(0, Math.floor(allData.length * 0.8));
          const unmatched = allData.slice(Math.floor(allData.length * 0.8));
          
          setCleanedData(cleaned);
          setUnmatchedData(unmatched);
          
          clearInterval(interval);
        }
        
        return newProgress;
      });
    }, 300);
  };

  const handleExport = (data: any[], filename: string, format: 'excel' | 'csv') => {
    // Mock export function
    console.log(`Exporting ${format.toUpperCase()}: ${filename}`, data);
    alert(`${format.toUpperCase()} export started for ${filename}`);
  };

  // Get friendly names for file types
  const getFileDisplayName = (fileType: keyof UploadedFiles): string => {
    const displayNames = {
      currentSystem: 'Current System Report',
      previousReference: 'Previous Reference',
      masterlistCurrent: 'Masterlist – Current',
      masterlistResigned: 'Masterlist – Resigned'
    };
    return displayNames[fileType];
  };

  // Get uploaded files for the preview selector
  const getUploadedFileOptions = () => {
    return Object.entries(uploadedFiles)
      .filter(([_, fileData]) => fileData !== undefined)
      .map(([fileType, _]) => ({
        value: fileType as keyof UploadedFiles,
        label: getFileDisplayName(fileType as keyof UploadedFiles)
      }));
  };

  // Set default preview file when files change
  useEffect(() => {
    const uploadedFileKeys = Object.keys(uploadedFiles).filter(key => uploadedFiles[key as keyof UploadedFiles]);
    if (uploadedFileKeys.length > 0 && !selectedPreviewFile) {
      setSelectedPreviewFile(uploadedFileKeys[0] as keyof UploadedFiles);
    }
  }, [uploadedFiles, selectedPreviewFile]);

  // Handle preview button click from file upload cards
  const handlePreviewFile = (fileType: keyof UploadedFiles) => {
    setSelectedPreviewFile(fileType);
    setCurrentStep(2);
    // Scroll to preview section
    setTimeout(() => {
      const previewSection = document.querySelector('[data-section="preview"]');
      if (previewSection) {
        previewSection.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const getCurrentDateTime = () => {
    return new Date().toLocaleString('en-PH', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStepBadgeVariant = (stepNumber: number) => {
    if (stepNumber < currentStep) return 'default';
    if (stepNumber === currentStep) return 'destructive';
    return 'secondary';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-red-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-[#CD1C18] to-[#9B1313] shadow-lg px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">CB</span>
            </div>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight">Employee Data Clean-Up Tool</h1>
              <p className="text-lg text-[#FFA896] font-bold mt-2">Chinabank Internal System</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Badge variant={getStepBadgeVariant(1)} className="bg-white/25 text-white border-white/40 text-base font-bold px-5 py-2.5 shadow-md">1. Upload</Badge>
            <Badge variant={getStepBadgeVariant(2)} className="bg-white/25 text-white border-white/40 text-base font-bold px-5 py-2.5 shadow-md">2. Preview</Badge>
            <Badge variant={getStepBadgeVariant(3)} className="bg-white/25 text-white border-white/40 text-base font-bold px-5 py-2.5 shadow-md">3. Clean-Up</Badge>
            <Badge variant={getStepBadgeVariant(4)} className="bg-white/25 text-white border-white/40 text-base font-bold px-5 py-2.5 shadow-md">4. Results</Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Instructions Section */}
        <section className="mb-8 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-blue-100">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent mb-5 tracking-tight">How to Use This Tool</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-lg text-gray-800">
                <div>
                  <h4 className="font-black text-xl text-[#9B1313] mb-4">📂 Step 1: Upload Files</h4>
                  <ul className="space-y-2.5 text-base">
                    <li>• Upload your Excel (.xlsx, .xls) or CSV files</li>
                    <li>• <strong>Current System Report:</strong> Latest employee data</li>
                    <li>• <strong>Previous Reference:</strong> Historical data for comparison</li>
                    <li>• <strong>Masterlist Current:</strong> Active employees reference</li>
                    <li>• <strong>Masterlist Resigned:</strong> Former employees list</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-black text-xl text-[#9B1313] mb-4">🔍 Step 2: Preview Data</h4>
                  <ul className="space-y-2.5 text-base">
                    <li>• Preview files immediately after upload</li>
                    <li>• Click "Preview" button on uploaded files</li>
                    <li>• Use search to find specific records</li>
                    <li>• Switch between uploaded files in preview</li>
                    <li>• Verify data structure and content</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-black text-xl text-[#9B1313] mb-4">⚙️ Step 3: Configure Clean-Up</h4>
                  <ul className="space-y-2.5 text-base">
                    <li>• Adjust fuzzy match threshold (50-100%)</li>
                    <li>• Higher % = more exact matching required</li>
                    <li>• Monitor progress and status updates</li>
                    <li>• Review summary statistics</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-black text-xl text-[#9B1313] mb-4">📊 Step 4: Export Results</h4>
                  <ul className="space-y-2.5 text-base">
                    <li>• <strong>Cleaned Report:</strong> Successfully matched records</li>
                    <li>• <strong>Unmatched for Review:</strong> Records needing manual review</li>
                    <li>• Export to CSV or Excel format</li>
                    <li>• Use results for further processing</li>
                  </ul>
                </div>
              </div>
              <div className="mt-4 p-5 bg-[#FFA896]/20 border-2 border-[#FFA896] rounded-lg">
                <p className="text-base text-[#9B1313] font-bold">
                  <strong className="font-black text-lg">⚠️ Important:</strong> This tool processes employee data. Ensure you have proper authorization and follow data privacy guidelines when handling sensitive information.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Step 1: File Upload */}
        <section className="mb-12 bg-white/60 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-full flex items-center justify-center shadow-lg">
              <span className="font-medium">1</span>
            </div>
            <div className="flex-1">
              <h2 className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent tracking-tight">File Upload</h2>
              <p className="text-lg text-gray-800 mt-3 font-bold">Upload your employee data files in Excel (.xlsx, .xls) or CSV format. All files should contain employee information with columns like Employee ID, Name, Department, etc.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FileUploadCard
              title="Current System Report"
              description="Latest employee data from your current system"
              requirement="Required"
              fileName={uploadedFiles.currentSystem?.file.name}
              isUploaded={!!uploadedFiles.currentSystem}
              isUploading={uploadingFiles.has('currentSystem')}
              onFileUpload={(file) => handleFileUpload('currentSystem', file)}
              onPreview={() => handlePreviewFile('currentSystem')}
            />
            <FileUploadCard
              title="Previous Reference"
              description="Historical employee data for comparison"
              requirement="Optional"
              fileName={uploadedFiles.previousReference?.file.name}
              isUploaded={!!uploadedFiles.previousReference}
              isUploading={uploadingFiles.has('previousReference')}
              onFileUpload={(file) => handleFileUpload('previousReference', file)}
              onPreview={() => handlePreviewFile('previousReference')}
            />
            <FileUploadCard
              title="Masterlist – Current"
              description="Reference list of active employees"
              requirement="Required"
              fileName={uploadedFiles.masterlistCurrent?.file.name}
              isUploaded={!!uploadedFiles.masterlistCurrent}
              isUploading={uploadingFiles.has('masterlistCurrent')}
              onFileUpload={(file) => handleFileUpload('masterlistCurrent', file)}
              onPreview={() => handlePreviewFile('masterlistCurrent')}
            />
            <FileUploadCard
              title="Masterlist – Resigned"
              description="Reference list of former employees"
              requirement="Optional"
              fileName={uploadedFiles.masterlistResigned?.file.name}
              isUploaded={!!uploadedFiles.masterlistResigned}
              isUploading={uploadingFiles.has('masterlistResigned')}
              onFileUpload={(file) => handleFileUpload('masterlistResigned', file)}
              onPreview={() => handlePreviewFile('masterlistResigned')}
            />
          </div>
          
          <div className="mt-6 bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-start space-x-3">
              <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="text-lg text-[#9B1313]">
                <p className="font-black mb-3 text-xl">📋 File Format Requirements:</p>
                <ul className="text-base space-y-2.5 font-semibold">
                  <li>• Accepted formats: Excel (.xlsx, .xls) or CSV (.csv)</li>
                  <li>• Each file should have column headers in the first row</li>
                  <li>• Common columns: Employee ID, Name, Department, Position, Email, Status</li>
                  <li>• Files can have different column structures - the system will adapt</li>
                  <li>• Maximum file size: 50MB per file</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <Separator className="my-8" />

        {/* Step 2: Data Preview */}
        {currentStep >= 2 && Object.keys(uploadedFiles).some(key => uploadedFiles[key as keyof UploadedFiles]) && (
          <section data-section="preview" className="mb-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 shadow-xl border border-blue-100">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-full flex items-center justify-center shadow-lg">
                <span className="font-medium">2</span>
              </div>
              <div className="flex-1">
                <h2 className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent tracking-tight">Data Preview</h2>
                <p className="text-lg text-gray-800 mt-3 font-bold">Review your uploaded data to ensure it's structured correctly. Use the search function to verify specific records before proceeding to the clean-up process.</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <label className="text-lg font-bold text-gray-800">Preview File:</label>
                  <Select 
                    value={selectedPreviewFile || ''} 
                    onValueChange={(value) => setSelectedPreviewFile(value as keyof UploadedFiles)}
                  >
                    <SelectTrigger className="w-48 bg-white border-blue-200 focus:border-blue-400">
                      <SelectValue placeholder="Select file to preview" />
                    </SelectTrigger>
                    <SelectContent>
                      {getUploadedFileOptions().map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <button
                  onClick={() => setCurrentStep(3)}
                  disabled={!uploadedFiles.currentSystem || !uploadedFiles.masterlistCurrent}
                  className="bg-gradient-to-r from-[#CD1C18] to-[#9B1313] text-white px-10 py-4 rounded-xl hover:from-[#9B1313] hover:to-[#38000A] transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed font-black text-lg"
                  title={!uploadedFiles.currentSystem || !uploadedFiles.masterlistCurrent ? "Upload required files (Current System Report & Masterlist Current) to continue" : ""}
                >
                  Continue to Clean-Up
                </button>
              </div>
            </div>
            
            <div className="space-y-8">
              {selectedPreviewFile && uploadedFiles[selectedPreviewFile] && (
                <DataPreviewTable
                  title={getFileDisplayName(selectedPreviewFile)}
                  data={uploadedFiles[selectedPreviewFile].data}
                  headers={uploadedFiles[selectedPreviewFile].headers}
                />
              )}
              
              {!selectedPreviewFile && (
                <div className="text-center py-12 text-gray-500">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p>Select a file from the dropdown above to preview its data</p>
                </div>
              )}
            </div>
            
            {getUploadedFileOptions().length > 0 && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="text-lg text-[#9B1313]">
                    <p className="font-black mb-3 text-xl">📋 Data Preview Tips:</p>
                    <ul className="text-base space-y-2.5 font-semibold">
                      <li>• Switch between uploaded files using the dropdown above</li>
                      <li>• Use the search function to find specific records</li>
                      <li>• Verify that column headers and data structure look correct</li>
                      <li>• Required files for clean-up: Current System Report & Masterlist Current</li>
                      <li>• You can upload additional files and preview them at any time</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {currentStep >= 2 && <Separator className="my-8" />}

        {/* Step 3: Clean-Up Controls */}
        {currentStep >= 3 && (
          <section className="mb-12 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl p-8 shadow-xl border border-orange-100">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full flex items-center justify-center shadow-lg">
                <span className="font-medium">3</span>
              </div>
              <div className="flex-1">
                <h2 className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent tracking-tight">Data Clean-Up</h2>
                <p className="text-lg text-gray-800 mt-3 font-bold">Configure matching settings and run the automated clean-up process. The system will match records across files using fuzzy logic algorithms and identify duplicates and inconsistencies.</p>
              </div>
            </div>
            
            <CleanupControls
              threshold={threshold}
              onThresholdChange={setThreshold}
              isRunning={isRunning}
              onRunCleanup={runCleanup}
              progress={progress}
              statusText={statusText}
              summaryCounts={summaryCounts}
            />
          </section>
        )}

        {currentStep >= 3 && <Separator className="my-8" />}

        {/* Step 4: Results */}
        {currentStep >= 4 && (
          <section className="mb-12 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-8 shadow-xl border border-green-100">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-full flex items-center justify-center shadow-lg">
                <span className="font-medium">4</span>
              </div>
              <div className="flex-1">
                <h2 className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent tracking-tight">Clean-Up Results</h2>
                <p className="text-lg text-gray-800 mt-3 font-bold">Review the cleaned data and export your results. The system has separated records into successfully matched data and items requiring manual review.</p>
              </div>
            </div>
            
            <ResultsSection
              cleanedData={cleanedData}
              unmatchedData={unmatchedData}
              headers={uploadedFiles.currentSystem?.headers || []}
              onExportExcel={(data, filename) => handleExport(data, filename, 'excel')}
              onExportCSV={(data, filename) => handleExport(data, filename, 'csv')}
            />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-[#38000A] to-[#9B1313] border-t border-[#CD1C18] px-6 py-6 mt-auto">
          <div className="flex items-center justify-between text-lg">
            <div className="flex items-center space-x-6 text-[#FFA896]">
              <span className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-[#FFA896] rounded-full animate-pulse"></div>
                <span className="font-bold">Last clean-up: {getCurrentDateTime()}</span>
              </span>
              <span className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-[#FFA896] rounded-full"></div>
                <span className="font-bold">User: System Administrator</span>
              </span>
            </div>
            <div className="flex items-center space-x-3 text-[#FFA896]">
              <div className="w-7 h-7 bg-gradient-to-r from-[#CD1C18] to-[#FFA896] rounded shadow-lg"></div>
              <span className="font-black text-xl">Chinabank Corporation</span>
            </div>
          </div>
      </footer>
    </div>
  );
}