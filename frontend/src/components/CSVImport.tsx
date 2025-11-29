import { useState, useRef, useEffect } from 'react';
import { Upload, CheckCircle, AlertCircle, X } from 'lucide-react';
import { api } from '@/services/api';

interface ImportResult {
  message: string;
  created: number;
  updated: number;
  errors: string[];
  total_processed: number;
}

export type { ImportResult };

export const CSVImport = ({ onImportSuccess }: { onImportSuccess?: (result: ImportResult) => void }) => {
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please select a CSV file');
      return;
    }

    setIsImporting(true);
    setError(null);

    try {
      const response = await api.importCSV(file);
      console.log('Import successful:', response);
      
      // Call success callback with the response
      if (onImportSuccess) {
        onImportSuccess(response);
      }
    } catch (err) {
      console.error('Import error:', err);
      setError(err instanceof Error ? err.message : 'Failed to import CSV');
    } finally {
      setIsImporting(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <>
      {/* Main Content */}
      <div className="space-y-4">
      {/* Import Button */}
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
        />
        <button
          onClick={handleButtonClick}
          disabled={isImporting}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Upload className="h-4 w-4" />
          {isImporting ? 'Importing...' : 'Import CSV'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 relative">
          <button
            onClick={clearError}
            className="absolute top-2 right-2 text-red-600 hover:text-red-800"
          >
            <X className="h-4 w-4" />
          </button>
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-900 mb-1">Import Failed</h3>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-sm text-muted-foreground">
        <p className="font-medium mb-1">CSV Format:</p>
        <p>Expected columns: Empresa, Ano, Setor, Consumo de Energia (MWh), Emissões de CO2 (toneladas)</p>
      </div>
      </div>
    </>
  );
};