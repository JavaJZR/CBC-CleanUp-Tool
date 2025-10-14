import React from 'react';
import { Upload, Check, FileText, Eye, Loader2 } from 'lucide-react';
import { Card } from './ui/card';

interface FileUploadCardProps {
  title: string;
  fileName?: string;
  isUploaded: boolean;
  isUploading?: boolean;
  onFileUpload: (file: File) => void;
  description?: string;
  requirement?: string;
  onPreview?: () => void;
}

export function FileUploadCard({ title, fileName, isUploaded, isUploading, onFileUpload, description, requirement, onPreview }: FileUploadCardProps) {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <Card className="border-2 border-dashed border-blue-200 hover:border-red-400 hover:bg-gradient-to-br hover:from-white hover:to-red-50 transition-all duration-300 p-6 bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl h-full">
      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleFileChange}
        className="hidden"
        id={`file-${title.replace(/\s+/g, '-').toLowerCase()}`}
      />
      
      {isUploading ? (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="text-center">
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center mb-3 shadow-lg">
                <Loader2 className="w-7 h-7 text-white animate-spin" />
              </div>
              <h3 className="font-medium text-gray-900 mb-1 text-center">{title}</h3>
              <p className="text-xs text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded-full mb-2">Parsing file...</p>
              {description && <p className="text-xs text-gray-500 text-center">{description}</p>}
            </div>
          </div>
        </div>
      ) : isUploaded ? (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="text-center">
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mb-3 shadow-lg">
                <Check className="w-7 h-7 text-white" />
              </div>
              <h3 className="font-medium text-gray-900 mb-1 text-center">{title}</h3>
              <p className="text-xs text-green-600 font-medium bg-green-50 px-2 py-1 rounded-full mb-2">{fileName}</p>
              {description && <p className="text-xs text-gray-500 text-center mb-3">{description}</p>}
              
              <div className="flex space-x-2 mt-2">
                <label
                  htmlFor={`file-${title.replace(/\s+/g, '-').toLowerCase()}`}
                  className="text-xs bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg cursor-pointer transition-colors duration-200 flex items-center space-x-1"
                >
                  <Upload className="w-3 h-3" />
                  <span>Replace</span>
                </label>
                {onPreview && (
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      onPreview();
                    }}
                    className="text-xs bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-lg transition-colors duration-200 flex items-center space-x-1"
                  >
                    <Eye className="w-3 h-3" />
                    <span>Preview</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <label
          htmlFor={`file-${title.replace(/\s+/g, '-').toLowerCase()}`}
          className="flex flex-col items-center justify-center h-full cursor-pointer"
        >
          <div className="text-center">
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center mb-3 shadow-lg hover:from-red-400 hover:to-red-500 transition-all duration-300">
                <Upload className="w-7 h-7 text-white" />
              </div>
              <h3 className="font-medium text-gray-900 mb-2 text-center">{title}</h3>
              {description && <p className="text-xs text-gray-600 text-center mb-2">{description}</p>}
              <p className="text-xs text-blue-600 font-medium bg-blue-50 px-3 py-1 rounded-full mb-2">Click to upload file</p>
              {requirement && (
                <div className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded border border-orange-200 text-center">
                  {requirement}
                </div>
              )}
            </div>
          </div>
        </label>
      )}
    </Card>
  );
}