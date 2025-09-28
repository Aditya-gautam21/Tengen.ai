'use client';

import type { LanguageModelUsage, UIMessage } from 'ai';
import {
  useRef,
  useEffect,
  useState,
  useCallback,
  type Dispatch,
  type SetStateAction,
  type ChangeEvent,
  memo,
  useMemo,
} from 'react';
import { toast } from 'sonner';
import { useLocalStorage, useWindowSize } from 'usehooks-ts';

import { ArrowUpIcon, PaperclipIcon, CpuIcon, StopIcon, ChevronDownIcon } from './icons';
import { PreviewAttachment } from './preview-attachment';
import { Button } from './ui/button';
import { SuggestedActions } from './suggested-actions';
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputToolbar,
  PromptInputTools,
  PromptInputSubmit,
  PromptInputModelSelect,
  PromptInputModelSelectContent,
} from './elements/prompt-input';
import { SelectItem } from '@/components/ui/select';
import * as SelectPrimitive from '@radix-ui/react-select';
import equal from 'fast-deep-equal';
import type { UseChatHelpers } from '@ai-sdk/react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowDown } from 'lucide-react';
import { useScrollToBottom } from '@/hooks/use-scroll-to-bottom';
import type { VisibilityType } from './visibility-selector';
import type { Attachment, ChatMessage } from '@/lib/types';
import { chatModels } from '@/lib/ai/models';
import { saveChatModelAsCookie } from '@/app/(chat)/actions';
import { startTransition } from 'react';
import { getContextWindow, normalizeUsage } from 'tokenlens';
import { Context } from './elements/context';
import { myProvider } from '@/lib/ai/providers';

// ...imports stay the same...

const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const apiBase = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000';

  try {
    const response = await fetch(`${apiBase}/files/upload`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      const { url, pathname, contentType } = data;

      return {
        url,
        name: pathname,
        contentType: contentType,
      };
    }
    const { error } = await response.json();
    toast.error(error);
  } catch (error) {
    toast.error('Failed to upload file, please try again!');
  }
};
