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
          <h3 className="text-lg font-medium bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-4">Clean-Up Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fuzzy Match Threshold: {threshold}%
              </label>
              <Slider
                value={[threshold]}
                onValueChange={(value) => onThresholdChange(value[0])}
                min={50}
                max={100}
                step={1}
                className="w-full"
              />
              <div className="text-xs text-gray-500 mt-2 space-y-1">
                <p>Higher values require more exact matches</p>
                <div className="bg-blue-50 p-2 rounded border border-blue-200">
                  <p className="font-medium text-blue-800">💡 Recommended Settings:</p>
                  <p className="text-blue-700">• 90-95%: Strict matching for clean data</p>
                  <p className="text-blue-700">• 80-89%: Balanced approach (recommended)</p>
                  <p className="text-blue-700">• 70-79%: Loose matching for messy data</p>
                </div>
              </div>
            </div>
            
            <Button
              onClick={onRunCleanup}
              disabled={isRunning}
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-medium py-4 shadow-lg hover:shadow-xl transition-all duration-200"
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
          <h3 className="text-lg font-medium bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">Status</h3>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
            
            <div className="text-sm text-gray-700">
              <p className="font-medium">{statusText}</p>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-gradient-to-br from-slate-50 to-slate-100 p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-2xl font-bold bg-gradient-to-r from-slate-600 to-slate-800 bg-clip-text text-transparent">{summaryCounts.total}</div>
                <div className="text-xs text-slate-600 font-medium">Total Records</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-4 rounded-xl border border-green-200 shadow-sm">
                <div className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{summaryCounts.matched}</div>
                <div className="text-xs text-green-700 font-medium">Matched</div>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-amber-100 p-4 rounded-xl border border-orange-200 shadow-sm">
                <div className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">{summaryCounts.unmatched}</div>
                <div className="text-xs text-orange-700 font-medium">For Review</div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}