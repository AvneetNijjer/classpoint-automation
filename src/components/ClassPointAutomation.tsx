
import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, CheckCircle, Clock, Play, Square, Settings } from "lucide-react";
import { toast } from "sonner";

interface AutomationConfig {
  classCode: string;
  studentName: string;
  answerStrategy: 'random' | 'always_a' | 'always_b' | 'always_c' | 'always_d';
  scheduleEnabled: boolean;
  scheduleTime: string;
  fallbackTime: string;
}

interface AutomationStatus {
  isRunning: boolean;
  currentStep: string;
  lastPollAnswered: string;
  totalPollsAnswered: number;
  errors: string[];
}

const ClassPointAutomation = () => {
  const [config, setConfig] = useState<AutomationConfig>({
    classCode: 'PHYS1E03',
    studentName: 'Avneet N.',
    answerStrategy: 'random',
    scheduleEnabled: true,
    scheduleTime: '09:02',
    fallbackTime: '09:10'
  });

  const [status, setStatus] = useState<AutomationStatus>({
    isRunning: false,
    currentStep: 'Ready to start',
    lastPollAnswered: 'None',
    totalPollsAnswered: 0,
    errors: []
  });

  const [backendConnected, setBackendConnected] = useState(false);

  // Get the correct API base URL
  const getApiUrl = (endpoint: string) => {
    // Try localhost first (for local development)
    const baseUrl = 'http://127.0.0.1:5000';
    return `${baseUrl}${endpoint}`;
  };

  // Check backend connection on component mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      console.log('Checking backend connection...');
      const response = await fetch(getApiUrl('/api/health'), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setBackendConnected(true);
        console.log('Backend connected successfully');
        toast.success("Backend connected successfully!");
      } else {
        throw new Error(`Backend responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setBackendConnected(false);
      toast.error("Backend connection failed. Make sure Python backend is running on port 5000.");
    }
  };

  const updateConfig = (key: keyof AutomationConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const startAutomation = async () => {
    if (!backendConnected) {
      toast.error("Backend not connected. Please start the Python backend first.");
      return;
    }

    try {
      console.log('Starting automation with config:', config);
      
      const response = await fetch(getApiUrl('/api/automation/start'), {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(config)
      });

      console.log('Start automation response status:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('Start automation result:', result);
        
        setStatus(prev => ({ 
          ...prev, 
          isRunning: true, 
          currentStep: 'Starting automation...',
          errors: []
        }));
        toast.success("Automation started successfully!");
        startStatusPolling();
      } else {
        const errorText = await response.text();
        console.error('Start automation failed:', errorText);
        throw new Error(`Failed to start automation: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Start automation error:', error);
      toast.error(`Failed to start automation: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const stopAutomation = async () => {
    try {
      console.log('Stopping automation...');
      
      const response = await fetch(getApiUrl('/api/automation/stop'), { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setStatus(prev => ({ ...prev, isRunning: false, currentStep: 'Stopped' }));
        toast.success("Automation stopped");
        console.log('Automation stopped successfully');
      } else {
        throw new Error(`Failed to stop: ${response.status}`);
      }
    } catch (error) {
      console.error('Stop automation error:', error);
      toast.error("Failed to stop automation");
    }
  };

  const startStatusPolling = () => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(getApiUrl('/api/automation/status'));
        if (response.ok) {
          const newStatus = await response.json();
          setStatus(newStatus);
          
          if (!newStatus.isRunning) {
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
      }
    }, 2000);
  };

  const getStatusColor = () => {
    if (!backendConnected) return "bg-red-500";
    if (status.isRunning) return "bg-green-500";
    if (status.errors.length > 0) return "bg-red-500";
    return "bg-gray-500";
  };

  const getStatusIcon = () => {
    if (!backendConnected) return <AlertCircle className="h-4 w-4" />;
    if (status.isRunning) return <CheckCircle className="h-4 w-4" />;
    if (status.errors.length > 0) return <AlertCircle className="h-4 w-4" />;
    return <Clock className="h-4 w-4" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">ClassPoint Automation</h1>
          <p className="text-gray-600">Automated participation for your online lectures</p>
        </div>

        {/* Backend Connection Status */}
        {!backendConnected && (
          <Card className="border-l-4 border-l-red-500 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <p className="font-medium">Backend Not Connected</p>
              </div>
              <p className="text-sm text-red-600 mt-1">
                Make sure to run: <code className="bg-red-100 px-2 py-1 rounded">python start_automation.py</code>
              </p>
              <Button 
                onClick={checkBackendConnection} 
                variant="outline" 
                size="sm" 
                className="mt-2 border-red-300 text-red-700 hover:bg-red-100"
              >
                Retry Connection
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Status Card */}
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
              Automation Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-gray-500">Current Step</p>
                <p className="font-medium">{status.currentStep}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-gray-500">Polls Answered</p>
                <p className="font-medium">{status.totalPollsAnswered}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-gray-500">Last Answer</p>
                <p className="font-medium">{status.lastPollAnswered}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-gray-500">Status</p>
                <Badge variant={status.isRunning ? "default" : "secondary"} className="flex items-center gap-1">
                  {getStatusIcon()}
                  {!backendConnected ? "Disconnected" : status.isRunning ? "Running" : "Stopped"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Configuration Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Configuration
              </CardTitle>
              <CardDescription>
                Set up your ClassPoint automation preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="classCode">Class Code</Label>
                <Input
                  id="classCode"
                  value={config.classCode}
                  onChange={(e) => updateConfig('classCode', e.target.value)}
                  placeholder="Enter class code (e.g., PHYS1E03)"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="studentName">Student Name</Label>
                <Input
                  id="studentName"
                  value={config.studentName}
                  onChange={(e) => updateConfig('studentName', e.target.value)}
                  placeholder="Enter your name"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="answerStrategy">Answer Strategy</Label>
                <Select value={config.answerStrategy} onValueChange={(value) => updateConfig('answerStrategy', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="random">Random Selection</SelectItem>
                    <SelectItem value="always_a">Always Answer A</SelectItem>
                    <SelectItem value="always_b">Always Answer B</SelectItem>
                    <SelectItem value="always_c">Always Answer C</SelectItem>
                    <SelectItem value="always_d">Always Answer D</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="scheduleEnabled"
                    checked={config.scheduleEnabled}
                    onCheckedChange={(checked) => updateConfig('scheduleEnabled', checked)}
                  />
                  <Label htmlFor="scheduleEnabled">Enable Scheduled Start</Label>
                </div>

                {config.scheduleEnabled && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="scheduleTime">Primary Time</Label>
                      <Input
                        id="scheduleTime"
                        type="time"
                        value={config.scheduleTime}
                        onChange={(e) => updateConfig('scheduleTime', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="fallbackTime">Fallback Time</Label>
                      <Input
                        id="fallbackTime"
                        type="time"
                        value={config.fallbackTime}
                        onChange={(e) => updateConfig('fallbackTime', e.target.value)}
                      />
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Control Card */}
          <Card>
            <CardHeader>
              <CardTitle>Control Panel</CardTitle>
              <CardDescription>
                Start or stop your automation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Button
                    onClick={startAutomation}
                    disabled={status.isRunning || !backendConnected}
                    className="flex-1"
                    size="lg"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Start Automation
                  </Button>
                  <Button
                    onClick={stopAutomation}
                    disabled={!status.isRunning}
                    variant="outline"
                    size="lg"
                  >
                    <Square className="h-4 w-4 mr-2" />
                    Stop
                  </Button>
                </div>

                {status.errors.length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-red-600">Recent Errors</Label>
                    <div className="bg-red-50 border border-red-200 rounded-md p-3 max-h-32 overflow-y-auto">
                      {status.errors.slice(-3).map((error, index) => (
                        <p key={index} className="text-sm text-red-700">{error}</p>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-sm text-gray-500 space-y-1">
                  <p><strong>How it works:</strong></p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Opens ClassPoint in a new browser tab</li>
                    <li>Automatically enters class code and name</li>
                    <li>Detects and answers polls as they appear</li>
                    <li>Runs continuously until stopped</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ClassPointAutomation;
