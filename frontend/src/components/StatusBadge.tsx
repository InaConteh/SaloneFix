import React from "react";
import {
  Clock,
  Search,
  CheckCircle,
  ArrowRight,
  Activity,
  FileText,
  AlertTriangle,
  Lock,
  XCircle,
  HelpCircle,
  GitMerge,
} from "lucide-react";
import type { ReportStatus, IncidentStatus } from "../types";

interface Props {
  status: ReportStatus | IncidentStatus | string;
}

export const StatusBadge: React.FC<Props> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case "SUBMITTED":
        return {
          icon: <Clock size={13} />,
          label: "Submitted",
          bg: "var(--status-submitted-bg)",
          color: "var(--status-submitted)",
        };
      case "UNDER_REVIEW":
        return {
          icon: <Search size={13} />,
          label: "Under Review",
          bg: "var(--status-review-bg)",
          color: "var(--status-review)",
        };
      case "NEEDS_CLARIFICATION":
        return {
          icon: <HelpCircle size={13} />,
          label: "Needs Clarification",
          bg: "var(--color-warning-bg)",
          color: "var(--color-warning)",
        };
      case "VERIFIED":
        return {
          icon: <CheckCircle size={13} />,
          label: "Verified",
          bg: "var(--status-verified-bg)",
          color: "var(--status-verified)",
        };
      case "MERGED":
        return {
          icon: <GitMerge size={13} />,
          label: "Merged",
          bg: "var(--status-assigned-bg)",
          color: "var(--status-assigned)",
        };
      case "REJECTED":
        return {
          icon: <XCircle size={13} />,
          label: "Rejected",
          bg: "var(--color-danger-bg)",
          color: "var(--color-danger)",
        };
      case "ASSIGNED":
        return {
          icon: <ArrowRight size={13} />,
          label: "Assigned",
          bg: "var(--status-assigned-bg)",
          color: "var(--status-assigned)",
        };
      case "IN_PROGRESS":
        return {
          icon: <Activity size={13} />,
          label: "In Progress",
          bg: "var(--status-progress-bg)",
          color: "var(--status-progress)",
        };
      case "RESOLUTION_UNDER_REVIEW":
        return {
          icon: <FileText size={13} />,
          label: "Resolution Review",
          bg: "var(--status-review-bg)",
          color: "var(--status-review)",
        };
      case "RESOLVED":
        return {
          icon: <CheckCircle size={13} />,
          label: "Resolved",
          bg: "var(--status-resolved-bg)",
          color: "var(--status-resolved)",
        };
      case "DISPUTED":
        return {
          icon: <AlertTriangle size={13} />,
          label: "Disputed",
          bg: "var(--status-disputed-bg)",
          color: "var(--status-disputed)",
        };
      case "CLOSED":
        return {
          icon: <Lock size={13} />,
          label: "Closed",
          bg: "var(--status-closed-bg)",
          color: "var(--status-closed)",
        };
      default:
        return {
          icon: <Clock size={13} />,
          label: status,
          bg: "var(--status-submitted-bg)",
          color: "var(--status-submitted)",
        };
    }
  };

  const { icon, label, bg, color } = getStatusConfig();

  return (
    <span
      className="badge"
      style={{
        backgroundColor: bg,
        color: color,
        border: `1px solid ${color}33`,
      }}
    >
      {icon}
      <span>{label}</span>
    </span>
  );
};
