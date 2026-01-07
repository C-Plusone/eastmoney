import { useState, useEffect, useRef } from 'react';
import { 
  Typography, 
  Button, 
  Paper, 
  CircularProgress, 
  Alert,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Grid,
  Tooltip
} from '@mui/material';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import HistoryIcon from '@mui/icons-material/History';
import ArticleIcon from '@mui/icons-material/Article';
import DownloadIcon from '@mui/icons-material/Download';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import html2canvas from 'html2canvas';
import { runSentimentAnalysis, fetchSentimentReports, fetchReportContent,  } from '../api';
import type { SentimentReportItem } from '../api';

export default function SentimentPage() {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<SentimentReportItem[]>([]);
  const [exporting, setExporting] = useState<boolean>(false);

  // Ref for export
  const reportRef = useRef<HTMLDivElement>(null);

  const loadHistory = async () => {
    try {
      const data = await fetchSentimentReports();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      const data = await runSentimentAnalysis();
      setReport(data.report);
      setSelectedFile(data.filename);
      await loadHistory(); // Refresh history
    } catch (err) {
      console.error(err);
      setError('Failed to generate sentiment analysis. Please check the backend logs.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectReport = async (filename: string) => {
    setLoading(true);
    setError(null);
    setSelectedFile(filename);
    try {
      const content = await fetchReportContent(filename);
      setReport(content);
    } catch (err) {
      console.error(err);
      setError('Failed to load report content.');
    } finally {
      setLoading(false);
    }
  };

  // Export report as image
  const handleExportImage = async () => {
      if (!reportRef.current || !report) return;
      
      setExporting(true);
      try {
          const exportWidth = 1200;
          const originalWidth = reportRef.current.style.width;
          const originalMaxWidth = reportRef.current.style.maxWidth;
          
          reportRef.current.style.width = `${exportWidth}px`;
          reportRef.current.style.maxWidth = `${exportWidth}px`;
          
          const canvas = await html2canvas(reportRef.current, {
              scale: 2,
              useCORS: true,
              backgroundColor: '#ffffff',
              logging: false,
              width: exportWidth,
              windowWidth: exportWidth
          });
          
          reportRef.current.style.width = originalWidth;
          reportRef.current.style.maxWidth = originalMaxWidth;
          
          const link = document.createElement('a');
          const fileName = `sentiment_${selectedFile || 'report'}.png`;
          link.download = fileName;
          link.href = canvas.toDataURL('image/png');
          link.click();
      } catch (error) {
          console.error('Failed to export image:', error);
      } finally {
          setExporting(false);
      }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 bg-white border-b border-slate-200 flex justify-between items-center shrink-0">
        <div>
          <Typography variant="h5" className="text-slate-900 font-bold tracking-tight mb-2">
            MARKET SENTIMENT
          </Typography>
          <Typography variant="body2" className="text-slate-500">
            Real-time emotion & cycle analysis
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={analyzing ? <CircularProgress size={20} color="inherit" /> : <AutoGraphIcon />}
          onClick={handleRunAnalysis}
          disabled={analyzing}
          sx={{
            backgroundColor: '#2563eb',
            textTransform: 'none',
            borderRadius: '8px',
            boxShadow: 'none',
            '&:hover': { backgroundColor: '#1d4ed8', boxShadow: 'none' }
          }}
        >
          {analyzing ? 'Analyzing...' : 'Run Analysis'}
        </Button>
      </div>

      <div className="flex-1 overflow-hidden flex">
        {/* Sidebar History */}
        <div className="w-64 bg-white border-r border-slate-200 overflow-y-auto flex flex-col shrink-0">
          <div className="p-4 border-b border-slate-100 bg-slate-50">
             <div className="flex items-center text-slate-600">
                <HistoryIcon fontSize="small" className="mr-2"/>
                <Typography variant="subtitle2" fontWeight="600">History</Typography>
             </div>
          </div>
          <List disablePadding>
            {history.map((item) => (
              <ListItem key={item.filename} disablePadding>
                <ListItemButton 
                  selected={selectedFile === item.filename}
                  onClick={() => handleSelectReport(item.filename)}
                  sx={{
                    borderLeft: selectedFile === item.filename ? '3px solid #2563eb' : '3px solid transparent',
                    backgroundColor: selectedFile === item.filename ? '#eff6ff' : 'transparent',
                    '&:hover': { backgroundColor: '#f8fafc' }
                  }}
                >
                  <ListItemText 
                    primary={item.date} 
                    secondary={item.filename}
                    primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 500 }}
                    secondaryTypographyProps={{ fontSize: '0.7rem', noWrap: true }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
            {history.length === 0 && (
              <div className="p-4 text-center text-slate-400 text-sm">
                No reports found.
              </div>
            )}
          </List>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: '8px' }}>
              {error}
            </Alert>
          )}
          
          {/* Export Bar */}
          {report && !loading && (
            <div className="flex justify-end mb-4">
                <Tooltip title="Download Image">
                    <Button
                        variant="outlined"
                        size="small"
                        startIcon={exporting ? <CircularProgress size={16} /> : <DownloadIcon />}
                        onClick={handleExportImage}
                        disabled={exporting}
                        className="border-slate-300 text-slate-600 hover:bg-slate-50 hover:border-slate-400"
                    >
                        {exporting ? 'Processing...' : 'Export Image'}
                    </Button>
                </Tooltip>
            </div>
          )}

          {loading ? (
             <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                <CircularProgress />
             </Box>
          ) : report ? (
            <Paper 
              ref={reportRef}
              elevation={0} 
              sx={{ 
                p: 5, 
                borderRadius: '12px', 
                border: '1px solid #e2e8f0',
                maxWidth: '900px',
                mx: 'auto',
                backgroundColor: '#ffffff'
              }}
            >
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {report}
                </ReactMarkdown>
              </div>
              {/* Footer for Export */}
              <div className="mt-8 pt-4 border-t border-slate-100 text-center">
                  <Typography variant="caption" className="text-slate-400 font-mono text-[10px] tracking-widest uppercase">
                      Generated by EastMoney Pro AI • Confidential • {new Date().getFullYear()}
                  </Typography>
              </div>
            </Paper>
          ) : (
            <Box 
              sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '60%',
                color: 'text.secondary',
              }}
            >
              <ArticleIcon sx={{ fontSize: 60, mb: 2, color: '#e2e8f0' }} />
              <Typography variant="h6" color="text.secondary">
                Select a report to view
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or click "Run Analysis" to generate a new one
              </Typography>
            </Box>
          )}
        </div>
      </div>
    </div>
  );
}