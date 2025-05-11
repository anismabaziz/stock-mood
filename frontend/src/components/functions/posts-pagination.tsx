import { Button } from "../ui/button";
import { ChevronRight, ChevronLeft, MoreHorizontal } from "lucide-react";

interface PostsPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function PostsPagination({
  currentPage,
  totalPages,
  onPageChange,
}: PostsPaginationProps) {
  const getPageNumbers = () => {
    const pages: (number | "...")[] = [];

    if (totalPages <= 3) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
      return pages;
    }

    if (currentPage <= 2) {
      pages.push(1, 2, "...", totalPages);
    } else if (currentPage >= totalPages - 1) {
      pages.push(1, "...", totalPages - 1, totalPages);
    } else {
      pages.push(1, "...", currentPage, "...", totalPages);
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="flex items-center justify-center space-x-2">
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        <ChevronLeft className="h-4 w-4" />
        <span className="sr-only">Previous page</span>
      </Button>

      {pageNumbers.map((page, index) => {
        if (page === "...") {
          return (
            <Button
              key={`ellipsis-${index}`}
              variant="outline"
              size="icon"
              disabled
            >
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">More pages</span>
            </Button>
          );
        }

        return (
          <Button
            key={page}
            variant={currentPage === page ? "default" : "outline"}
            onClick={() => onPageChange(page)}
            className="w-9 h-9"
          >
            {page}
          </Button>
        );
      })}

      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        <ChevronRight className="h-4 w-4" />
        <span className="sr-only">Next page</span>
      </Button>
    </div>
  );
}
