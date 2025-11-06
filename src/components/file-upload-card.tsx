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
              <h3 className="font-black text-xl text-gray-900 mb-3 text-center">{title}</h3>
              <p className="text-base text-[#CD1C18] font-black bg-[#FFA896]/20 px-4 py-2 rounded-full mb-3 border-2 border-[#FFA896]">Parsing file...</p>
              {description && <p className="text-base text-gray-700 text-center font-bold">{description}</p>}
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
              <h3 className="font-black text-xl text-gray-900 mb-3 text-center">{title}</h3>
              <p className="text-base text-[#9B1313] font-black bg-[#FFA896]/20 px-4 py-2 rounded-full mb-3 border-2 border-[#FFA896]">{fileName}</p>
              {description && <p className="text-base text-gray-700 text-center mb-4 font-bold">{description}</p>}
              
              <div className="flex space-x-2 mt-2">
                <label
                  htmlFor={`file-${title.replace(/\s+/g, '-').toLowerCase()}`}
                  className="text-base font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] hover:from-[#9B1313] hover:to-[#38000A] text-white px-6 py-3 rounded-lg cursor-pointer transition-all duration-200 flex items-center space-x-2 shadow-lg"
                >
                  <Upload className="w-5 h-5" />
                  <span>Replace</span>
                </label>
                {onPreview && (
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      onPreview();
                    }}
                    className="text-base font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] hover:from-[#9B1313] hover:to-[#38000A] text-white px-6 py-3 rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-lg"
                  >
                    <Eye className="w-5 h-5" />
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
              <h3 className="font-black text-xl text-gray-900 mb-3 text-center">{title}</h3>
              {description && <p className="text-base text-gray-700 text-center mb-4 font-bold">{description}</p>}
              <p className="text-base text-[#CD1C18] font-black bg-[#FFA896]/20 px-5 py-2.5 rounded-full mb-4 border-2 border-[#FFA896]">Click to upload file</p>
              {requirement && (
                <div className="text-base text-[#9B1313] bg-[#FFA896]/20 px-4 py-3 rounded-lg border-2 border-[#FFA896] text-center font-black">
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