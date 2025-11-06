import React from 'react';
import { Play, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Card } from './ui/card';
import { Progress } from './ui/progress';

interface CleanupControlsProps {
  threshold: number;
  onThresholdChange: (value: number) => void;
  isRunning: boolean;
  onRunCleanup: () => void;
  progress: number;
  statusText: string;
  summaryCounts: {
    total: number;
    matched: number;
    unmatched: number;
  };
}

export function CleanupControls({
  threshold,
  onThresholdChange,
  isRunning,
  onRunCleanup,
  progress,
  statusText,
  summaryCounts
}: CleanupControlsProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 bg-gradient-to-br from-white to-orange-50 border border-orange-200 shadow-lg">
          <h3 className="text-2xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent mb-5 tracking-tight">Clean-Up Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-lg font-black text-gray-900 mb-4">
                Fuzzy Match Threshold: <span className="text-[#CD1C18] font-black text-xl">{threshold}%</span>
              </label>
              <Slider
                value={[threshold]}
                onValueChange={(value) => onThresholdChange(value[0])}
                min={50}
                max={100}
                step={1}
                className="w-full"
              />
              <div className="text-base text-gray-700 mt-4 space-y-3">
                <p className="font-bold text-lg">Higher values require more exact matches</p>
                <div className="bg-[#FFA896]/20 p-5 rounded-lg border-2 border-[#FFA896]">
                  <p className="font-black text-xl text-[#9B1313] mb-3">💡 Recommended Settings:</p>
                  <p className="text-[#9B1313] font-bold text-base">• 90-95%: Strict matching for clean data</p>
                  <p className="text-[#9B1313] font-bold text-base">• 80-89%: Balanced approach (recommended)</p>
                  <p className="text-[#9B1313] font-bold text-base">• 70-79%: Loose matching for messy data</p>
                </div>
              </div>
            </div>
            
            <Button
              onClick={onRunCleanup}
              disabled={isRunning}
              className="w-full bg-gradient-to-r from-[#CD1C18] to-[#9B1313] hover:from-[#9B1313] hover:to-[#38000A] text-white font-black py-5 shadow-lg hover:shadow-xl transition-all duration-200 text-lg"
              size="lg"
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Running Clean-Up...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Run Clean-Up
                </>
              )}
            </Button>
          </div>
        </Card>
        
        <Card className="p-6 bg-gradient-to-br from-white to-blue-50 border border-blue-200 shadow-lg">
          <h3 className="text-2xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent mb-5 tracking-tight">Status</h3>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-lg text-gray-900 mb-3">
                <span className="font-black">Progress</span>
                <span className="font-black text-[#CD1C18] text-xl">{progress}%</span>
              </div>
              <Progress value={progress} className="h-4" />
            </div>
            
            <div className="text-lg text-gray-900">
              <p className="font-black">{statusText}</p>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-gradient-to-br from-[#FFA896]/30 to-[#FFA896]/10 p-6 rounded-xl border-2 border-[#FFA896] shadow-lg">
                <div className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent">{summaryCounts.total}</div>
                <div className="text-base text-[#9B1313] font-black mt-2">Total Records</div>
              </div>
              <div className="bg-gradient-to-br from-[#FFA896]/30 to-[#FFA896]/10 p-6 rounded-xl border-2 border-[#FFA896] shadow-lg">
                <div className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent">{summaryCounts.matched}</div>
                <div className="text-base text-[#9B1313] font-black mt-2">Matched</div>
              </div>
              <div className="bg-gradient-to-br from-[#FFA896]/30 to-[#FFA896]/10 p-6 rounded-xl border-2 border-[#FFA896] shadow-lg">
                <div className="text-4xl font-black bg-gradient-to-r from-[#CD1C18] to-[#9B1313] bg-clip-text text-transparent">{summaryCounts.unmatched}</div>
                <div className="text-base text-[#9B1313] font-black mt-2">For Review</div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}